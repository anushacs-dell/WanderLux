from django.db import models

# Create your models here.
from django.contrib.auth.models import User
 
 
class Destination(models.Model):
    CATEGORY_CHOICES = [
        ('beach', 'Beach'),
        ('mountain', 'Mountain'),
        ('city', 'City'),
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('wildlife', 'Wildlife'),
    ]
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='city')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.name}, {self.country}"
 
 
class TravelPackage(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('challenging', 'Challenging'),
    ]
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='packages')
    description = models.TextField()
    duration_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_group_size = models.IntegerField(default=10)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    includes = models.TextField(help_text="Comma-separated list of inclusions", blank=True)
    excludes = models.TextField(help_text="Comma-separated list of exclusions", blank=True)
    itinerary = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.title
 
    def get_includes_list(self):
        return [i.strip() for i in self.includes.split(',') if i.strip()]
 
    def get_excludes_list(self):
        return [e.strip() for e in self.excludes.split(',') if e.strip()]
 
 
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='bookings')
    travel_date = models.DateField()
    num_travelers = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return f"{self.user.username} - {self.package.title} ({self.travel_date})"
 
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.package.price * self.num_travelers
        super().save(*args, **kwargs)
 
 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_pic = models.URLField(blank=True, null=True)
    passport_number = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
 
    def __str__(self):
        return f"{self.user.username}'s Profile"
 
 
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.user.username} - {self.package.title} ({self.rating}★)"
 
 
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.name} - {self.subject}"
 
 
class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
 
    def __str__(self):
        return self.email
 