from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django import forms
from django.utils import timezone
import datetime
# from django_google_maps import fields as map_fields
# Create your models here.

# A less-detailed version of a class, this is meant to be used when searching
# This should speed up search requests.
class Class(models.Model):
    instructor_name = models.CharField(max_length=200, default="")
    instructor_email = models.CharField(max_length=200, default="")
    course_number = models.IntegerField(default = 0)
    semester_code = models.IntegerField(default = 0)
    course_section = models.CharField(max_length=200, default="")
    subject = models.CharField(max_length=10, default="")
    catalog_number = models.CharField(max_length=200, default="")
    description = models.CharField(max_length=5000, default="")
    units = models.CharField(max_length=10, default="")
    component = models.CharField(max_length=10, default="")
    class_capacity = models.IntegerField(default = 0)
    wait_list = models.IntegerField(default = 0)
    wait_cap = models.IntegerField(default = 0)
    enrollment_total = models.IntegerField(default = 0)
    enrollment_available = models.IntegerField(default = 0)
    topic = models.CharField(max_length=200, default="")
    meetings_days = models.CharField(max_length=15, default="")
    meetings_start_time = models.SlugField(max_length = 10, default="")
    meetings_end_time = models.SlugField(max_length = 10, default="")
    facility_description = models.CharField(max_length=50, default="")

    def str(self) -> str:
        return super().str()

class Dept(models.Model):
    subject = models.CharField(max_length=4)
    def str(self) -> str:
        return subject

# each user (defined by google login) has a single profile and each profile has some schedules and many classes
# so a profile just represents for a user
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Class)
    # add a friend attribute to profile
    friends = models.ManyToManyField(User, related_name='friends')

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class ProfileForm(forms.ModelForm):
    class Meta: 
        model = Profile
        fields = ('courses',)

# This friend request model will store the friend requests info i.e who send request to whom.
class Friend_Request(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)

# need a schedule model to store the courses the user adds to build the schedule
class Schedule(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="")
    courses = models.ManyToManyField(Class)

    # similar code to a comment so that the entire schedule can be upvoted or downvoted
    ups = models.IntegerField(default = 0)
    downs = models.IntegerField(default = 0)
    voted_users = models.ManyToManyField(User)
    
    @receiver(post_save, sender=User)
    def create_profile_schedule(sender, instance, created, **kwargs):
        if created:
            Schedule.objects.create(profile=instance.profile)

    @receiver(post_save, sender=User)
    def save_profile_schedule(sender, instance, **kwargs):
        instance.profile.schedule.save()

# comments class include contents and ups or downs
class Comment(models.Model):
    # one comment belongs to a schedule but one schedule can have multiple comments
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    content = models.CharField(max_length=5000, default="")
    ups = models.IntegerField(default = 0)
    downs = models.IntegerField(default = 0)
    voted_users = models.ManyToManyField(User)
    # need to record the time the comment is published so that we can list them by the time they were created, and it won't be affected by the votes
    pub_date = models.DateTimeField('date published')

class ScheduleForm(forms.ModelForm):
    class Meta: 
        model = Schedule
        fields = ('courses', 'name', )

# create a speical model to store all courses information without change
# class All_class(models.Model):
#     course_number = models.IntegerField(default = 0)
#     catalog_number = models.SlugField(max_length=12)
#     instructor_name = models.CharField(max_length=200)
#     name = models.CharField(max_length=200)
#     subject = models.CharField(max_length=4)
#     description = models.CharField(max_length=5000)
#     units = models.CharField(max_length=2)
#     enrollment_available = models.IntegerField(default = 0)
#     class_capacity = models.IntegerField(default = 0)
#     wait_list = models.IntegerField(default = 0)
#     wait_cap = models.IntegerField(default = 0)
#     meetings_days = models.CharField(max_length=15)
#     def str(self) -> str:
#         return super().str()

# class Facility(models.Model):
#     address = map_fields.AddressField(max_length=200)
#     geolocation = map_fields.GeoLocationField(max_length=100)