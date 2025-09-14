from django.db import models
from django.conf import settings


class Quote(models.Model):
    CAR_CHOICES = [
    ('small', 'Small'),
    ('sedan', 'Sedan'),
    ('suv', 'SUV'),
    ]

    TARIFF_CHOICES = [
      ('basic','Basic'),
      ('silver','Silver'),
      ('gold','Gold'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quotes')
    tariff = models.CharField(max_length=20, choices=TARIFF_CHOICES)
    age = models.PositiveIntegerField()
    driving_experience = models.PositiveIntegerField()  
    car_type = models.CharField(max_length=50, choices=CAR_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tariff']),
        ]
    
    def __str__(self):
        return f"Quote #{self.pk} - {self.user} - {self.total_price}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, db_index=True)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tariff = models.CharField(max_length=20, choices=Quote.TARIFF_CHOICES, default='basic')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['quote']),
            models.Index(fields=['tariff']),
        ]

    def __str__(self):
        return f"Application #{self.pk} - {self.full_name}"
