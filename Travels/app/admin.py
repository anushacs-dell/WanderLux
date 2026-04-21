from django.contrib import admin
from .models import Destination, TravelPackage, Booking, UserProfile, Review, ContactMessage, Newsletter

admin.site.site_header = "WanderLux Travel Admin"
admin.site.site_title = "WanderLux"
admin.site.index_title = "Travel Management"

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'category', 'featured', 'rating']
    list_filter = ['category', 'featured']
    search_fields = ['name', 'country']
    list_editable = ['featured']

@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'duration_days', 'price', 'available', 'featured']
    list_filter = ['available', 'featured', 'difficulty']
    search_fields = ['title']
    list_editable = ['available', 'featured']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'travel_date', 'num_travelers', 'total_price', 'status']
    list_filter = ['status']
    search_fields = ['user__username', 'package__title']
    list_editable = ['status']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'nationality']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'rating', 'created_at']
    list_filter = ['rating']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    list_editable = ['is_read']

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'active']