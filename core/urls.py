from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    QuoteListCreateView,
    QuoteDetailView,
    ApplicationListCreateView,
    ApplicationDetailView,
    LogoutUserView,
)

app_name = "core" 

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),

    path('quotes/', QuoteListCreateView.as_view(), name='quote-list-create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote-detail'),

    path('applications/', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('applications/<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
]
