from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Quote, Application




# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, validators=[UniqueValidator(User.objects.all(), "This email is already used.")])

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'username': {'validators': [UniqueValidator(User.objects.all(), "This username is already taken.")]},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Quote Serializers
class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = '__all__'
        read_only_fields = ('id', 'user', 'base_price', 'total_price', 'created_at')


class QuoteCreateSerializer(serializers.ModelSerializer):
    tariff = serializers.ChoiceField(choices=Quote.TARIFF_CHOICES)
    car_type = serializers.ChoiceField(choices=Quote.CAR_CHOICES)
    age = serializers.IntegerField(min_value=16)
    driving_experience = serializers.IntegerField(min_value=0)

    class Meta:
        model = Quote
        fields = ('tariff', 'age', 'driving_experience', 'car_type')

    def validate(self, data):
        age = data.get('age')
        exp = data.get('driving_experience')
        if age is not None and exp is not None:
            max_possible_exp = age - 16
            if exp > max_possible_exp:
                raise serializers.ValidationError({"driving_experience": "Experience is not realistic for given age"})
        return data

    def create(self, validated_data):
        # calculation using Decimal for precision
        base_map = {
            'basic': Decimal('1000.00'),
            'silver': Decimal('1200.00'),
            'gold': Decimal('1500.00'),
        }
        car_coef = {
            'small': Decimal('1.00'),
            'sedan': Decimal('1.10'),
            'suv': Decimal('1.20'),
        }

        tariff = validated_data['tariff']
        age = validated_data['age']
        exp = validated_data['driving_experience']
        car = validated_data['car_type']

        base_price = base_map.get(tariff, Decimal('1000.00'))

        # coefficients algrithm
        age_coef = Decimal('1.00')
        if age < 25:
            age_coef = Decimal('1.30')
        elif age >= 60:
            age_coef = Decimal('1.20')

        exp_coef = Decimal('1.00')
        if exp < 2:
            exp_coef = Decimal('1.40')
        elif exp <= 5:
            exp_coef = Decimal('1.20')

        car_multiplier = car_coef.get(car, Decimal('1.00'))

        coeff = age_coef * exp_coef * car_multiplier
        total = (base_price * coeff).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        validated_data['base_price'] = base_price
        validated_data['total_price'] = total

        # get user
        user = None
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user and request.user.is_authenticated:
            user = request.user

        
        validated_data.pop('user', None)

        if user is None:
            # fallback>> if user not provided
            raise serializers.ValidationError({"user": "Authenticated user required to create quote"})

        # create Quote instance
        return Quote.objects.create(user=user, **validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    quote = serializers.PrimaryKeyRelatedField(queryset=Quote.objects.all())
    full_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = Application
        fields = ('id', 'user', 'quote', 'full_name', 'phone', 'email', 'tariff', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'tariff', 'status', 'created_at', 'updated_at')

    def validate_quote(self, value: Quote):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to use quote")
        if value.user_id != request.user.id:
            raise serializers.ValidationError("You can only create application for your own quote")
        return value

    def create(self, validated_data):
        validated_data.pop('user', None)

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError({"user": "Authenticated user required"})

        quote = validated_data.get('quote')
        validated_data['tariff'] = quote.tariff

        # if full_name/email not provided - try to take from user
        if not validated_data.get('full_name'):
            # build from first + last name or username
            full_name = f"{user.first_name} {user.last_name}".strip()
            if not full_name:
                full_name = getattr(user, 'username', '')
            validated_data['full_name'] = full_name

        if not validated_data.get('email'):
            validated_data['email'] = user.email


        # create application whith request.user as owner 
        return Application.objects.create(user=user, **validated_data)
