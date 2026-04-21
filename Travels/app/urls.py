from django.urls import path
from . import views

urlpatterns = [
    # User side
    path('', views.home, name='home'),
    path('destinations/', views.destinations, name='destinations'),
    path('destinations/<int:pk>/', views.destination_detail, name='destination_detail'),
    path('packages/', views.packages, name='packages'),
    path('packages/<int:pk>/', views.package_detail, name='package_detail'),
    path('packages/<int:pk>/book/', views.book_package, name='book_package'),
    path('packages/<int:pk>/review/', views.add_review, name='add_review'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('contact/', views.contact, name='contact'),
    path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Admin side
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/bookings/', views.admin_bookings, name='admin_bookings'),
    path('manage/bookings/<int:pk>/update/', views.admin_update_booking, name='admin_update_booking'),
    path('manage/destinations/', views.admin_destinations, name='admin_destinations'),
    path('manage/destinations/add/', views.admin_add_destination, name='admin_add_destination'),
    path('manage/destinations/<int:pk>/edit/', views.admin_edit_destination, name='admin_edit_destination'),
    path('manage/destinations/<int:pk>/delete/', views.admin_delete_destination, name='admin_delete_destination'),
    path('manage/packages/', views.admin_packages, name='admin_packages'),
    path('manage/packages/add/', views.admin_add_package, name='admin_add_package'),
    path('manage/packages/<int:pk>/edit/', views.admin_edit_package, name='admin_edit_package'),
    path('manage/packages/<int:pk>/delete/', views.admin_delete_package, name='admin_delete_package'),
    path('manage/users/', views.admin_users, name='admin_users'),
    path('manage/messages/', views.admin_messages, name='admin_messages'),
    path('manage/messages/<int:pk>/read/', views.admin_mark_message_read, name='admin_mark_message_read'),
]