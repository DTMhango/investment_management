from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('about/', views.about, name='about'),
    path('register/', views.register_user, name='register'),
    path('client/', views.all_client_data, name='client'),
    path('contribution/', views.all_contribution_data, name='client_contribution'),
    path('investment/', views.all_investment_data, name='client_investment'),
    path('individual/client/<int:pk>/', views.individual_client_data, name='individual_client'),
    path('individual/contributions/<int:pk>/', views.individual_contribution_data, name='individual_contributions'),
    path('individual/investments/<int:pk>/', views.individual_investment_data, name='individual_investments'),
    path('create_client/', views.create_client, name='create_client'),
    path('update_records/', views.update_records, name='update_records'),
    path('individual/<int:client_id>/create_contribution/', views.create_contribution, name='create_contribution'),
    path('individual/<int:client_id>/create_investment', views.create_investment, name='create_investment'),
]
