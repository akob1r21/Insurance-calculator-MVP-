# core/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.db import DatabaseError
from rest_framework_simplejwt.exceptions import TokenError
from .models import Quote, Application
from .serializers import (
    RegisterSerializer,
    QuoteSerializer,
    QuoteCreateSerializer,
    ApplicationSerializer,
)



# Auth views
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Username or password incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'user_id': user.id,
        }, status=status.HTTP_200_OK)




class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token required'}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully'}, status=205)
        except TokenError:
            return Response({'detail': 'Invalid or expired token'}, status=400)
        except DatabaseError:
            
            return Response({
                'status': 'error',
                'message': 'Server misconfiguration',
                'errors': {'detail': ['Token blacklist tables are missing. Run migrations on the server.']}
            }, status=500)


# Quote views
class QuoteListCreateView(generics.ListCreateAPIView):
    serializer_class = QuoteCreateSerializer  
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Quote.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class QuoteDetailView(generics.RetrieveAPIView):
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # owner-only can access
        return Quote.objects.filter(user=self.request.user)


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


class ApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)
