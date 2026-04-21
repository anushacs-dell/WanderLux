from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Destination, TravelPackage, Booking, UserProfile, Review, ContactMessage, Newsletter
from .forms import (UserRegisterForm, UserProfileForm, BookingForm, ReviewForm,
                    ContactForm, NewsletterForm, DestinationForm, TravelPackageForm)


def is_admin(user):
    return user.is_staff or user.is_superuser


# ─── USER SIDE VIEWS ───────────────────────────────────────────────────────────

def home(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    featured_destinations = Destination.objects.filter(featured=True)[:6]
    featured_packages = TravelPackage.objects.filter(featured=True, available=True)[:6]
    all_packages = TravelPackage.objects.filter(available=True)[:8]
    categories = Destination.CATEGORY_CHOICES
    stats = {
        'destinations': Destination.objects.count(),
        'packages': TravelPackage.objects.count(),
        'bookings': Booking.objects.filter(status='completed').count(),
        'travelers': User.objects.count(),
    }
    return render(request, 'travel_app/home.html', {
        'featured_destinations': featured_destinations,
        'featured_packages': featured_packages,
        'all_packages': all_packages,
        'categories': categories,
        'stats': stats,
    })


def destinations(request):
    qs = Destination.objects.all()
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    if category:
        qs = qs.filter(category=category)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(country__icontains=search))
    return render(request, 'travel_app/destinations.html', {
        'destinations': qs,
        'categories': Destination.CATEGORY_CHOICES,
        'selected_category': category,
        'search': search,
    })


def destination_detail(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    packages = TravelPackage.objects.filter(destination=destination, available=True)
    return render(request, 'travel_app/destination_detail.html', {
        'destination': destination,
        'packages': packages,
    })


def packages(request):
    qs = TravelPackage.objects.filter(available=True)
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    duration = request.GET.get('duration', '')
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(destination__name__icontains=search))
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    if duration:
        qs = qs.filter(duration_days__lte=int(duration))
    return render(request, 'travel_app/packages.html', {'packages': qs, 'search': search})


def package_detail(request, pk):
    package = get_object_or_404(TravelPackage, pk=pk)
    reviews = Review.objects.filter(package=package).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    booking_form = BookingForm()
    review_form = ReviewForm()
    user_booked = False
    if request.user.is_authenticated:
        user_booked = Booking.objects.filter(user=request.user, package=package, status__in=['confirmed', 'completed']).exists()
    return render(request, 'travel_app/package_detail.html', {
        'package': package,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'booking_form': booking_form,
        'review_form': review_form,
        'user_booked': user_booked,
    })


@login_required
def book_package(request, pk):
    package = get_object_or_404(TravelPackage, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.package = package
            booking.total_price = package.price * booking.num_travelers
            booking.save()
            messages.success(request, f'Booking confirmed for {package.title}!')
            return redirect('my_bookings')
    return redirect('package_detail', pk=pk)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'travel_app/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('my_bookings')


@login_required
def add_review(request, pk):
    package = get_object_or_404(TravelPackage, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.package = package
            review.save()
            messages.success(request, 'Review submitted!')
    return redirect('package_detail', pk=pk)


@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'travel_app/dashboard.html', {
        'bookings': bookings,
        'profile': profile,
        'total_bookings': bookings.count(),
        'confirmed': bookings.filter(status='confirmed').count(),
        'pending': bookings.filter(status='pending').count(),
        'completed': bookings.filter(status='completed').count(),
    })


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Update user fields
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'travel_app/edit_profile.html', {'form': form, 'profile': profile})


def contact(request):
    tags = ["Beach", "Mountain", "Adventure", "Cultural", "Wildlife", "Honeymoon", "Family", "Luxury", "Budget"]
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message sent! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'travel_app/contact.html',
        {'form': form,
         'tags': tags,
         })


def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        obj, created = Newsletter.objects.get_or_create(email=email)
        if created:
            messages.success(request, 'Subscribed to newsletter!')
        else:
            messages.info(request, 'Already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', '/'))





def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'travel_app/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            # ❗ Block admin users from frontend
            if user.is_superuser:
                messages.error(request, "Admin users must log in via admin panel.")
                return redirect('login')

            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'travel_app/login.html')


def user_logout(request):
    logout(request)
    return redirect('home')


# ─── ADMIN SIDE VIEWS ──────────────────────────────────────────────────────────

@user_passes_test(is_admin, login_url='/login/')
def admin_dashboard(request):
    stats = {
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'confirmed_bookings': Booking.objects.filter(status='confirmed').count(),
        'total_revenue': Booking.objects.filter(status__in=['confirmed', 'completed']).aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_destinations': Destination.objects.count(),
        'total_packages': TravelPackage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }
    recent_bookings = Booking.objects.order_by('-booking_date')[:10]
    recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
    return render(request, 'travel_app/admin/dashboard.html', {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'recent_messages': recent_messages,
    })


@user_passes_test(is_admin, login_url='/login/')
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-booking_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'travel_app/admin/bookings.html', {
        'bookings': bookings, 'status_filter': status_filter
    })


@user_passes_test(is_admin, login_url='/login/')
def admin_update_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.status = request.POST.get('status', booking.status)
        booking.save()
        messages.success(request, 'Booking updated!')
    return redirect('admin_bookings')


@user_passes_test(is_admin, login_url='/login/')
def admin_destinations(request):
    destinations = Destination.objects.all().order_by('-created_at')
    return render(request, 'travel_app/admin/destinations.html', {'destinations': destinations})


@user_passes_test(is_admin, login_url='/login/')
def admin_add_destination(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination added!')
            return redirect('admin_destinations')
    else:
        form = DestinationForm()
    return render(request, 'travel_app/admin/destination_form.html', {'form': form, 'action': 'Add'})


@user_passes_test(is_admin, login_url='/login/')
def admin_edit_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination updated!')
            return redirect('admin_destinations')
    else:
        form = DestinationForm(instance=destination)
    return render(request, 'travel_app/admin/destination_form.html', {'form': form, 'action': 'Edit'})


@user_passes_test(is_admin, login_url='/login/')
def admin_delete_destination(request, pk):
    destination = get_object_or_404(Destination, pk=pk)
    destination.delete()
    messages.success(request, 'Destination deleted!')
    return redirect('admin_destinations')


@user_passes_test(is_admin, login_url='/login/')
def admin_packages(request):
    packages = TravelPackage.objects.all().order_by('-created_at')
    return render(request, 'travel_app/admin/packages.html', {'packages': packages})


@user_passes_test(is_admin, login_url='/login/')
def admin_add_package(request):
    if request.method == 'POST':
        form = TravelPackageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package added!')
            return redirect('admin_packages')
    else:
        form = TravelPackageForm()
    return render(request, 'travel_app/admin/package_form.html', {'form': form, 'action': 'Add'})


@user_passes_test(is_admin, login_url='/login/')
def admin_edit_package(request, pk):
    package = get_object_or_404(TravelPackage, pk=pk)
    if request.method == 'POST':
        form = TravelPackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, 'Package updated!')
            return redirect('admin_packages')
    else:
        form = TravelPackageForm(instance=package)
    return render(request, 'travel_app/admin/package_form.html', {'form': form, 'action': 'Edit'})


@user_passes_test(is_admin, login_url='/login/')
def admin_delete_package(request, pk):
    package = get_object_or_404(TravelPackage, pk=pk)
    package.delete()
    messages.success(request, 'Package deleted!')
    return redirect('admin_packages')


@user_passes_test(is_admin, login_url='/login/')
def admin_users(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'travel_app/admin/users.html', {'users': users})


@user_passes_test(is_admin, login_url='/login/')
def admin_messages(request):
    msgs = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'travel_app/admin/messages.html', {'msgs': msgs})


@user_passes_test(is_admin, login_url='/login/')
def admin_mark_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect('admin_messages')