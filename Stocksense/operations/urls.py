from django.urls import path
from . import views

urlpatterns = [
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/new/', views.receipt_create, name='receipt_create'),
    path('receipts/<int:pk>/', views.receipt_detail, name='receipt_detail'),

    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/new/', views.delivery_create, name='delivery_create'),
    path('deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),

    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/new/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/', views.transfer_detail, name='transfer_detail'),

    path('adjustments/', views.adjustment_list, name='adjustment_list'),
    path('adjustments/new/', views.adjustment_create, name='adjustment_create'),
    path('adjustments/<int:pk>/', views.adjustment_detail, name='adjustment_detail'),
]