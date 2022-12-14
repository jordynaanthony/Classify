from django.contrib import admin
# from django_google_maps import widgets as map_widgets
# from django_google_maps import fields as map_fields


# Register your models here.
from .models import Class, Dept, Profile, ProfileForm, Schedule, Friend_Request, Comment

class ClassAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,               {'fields': ['subject']}),
    #     ('Course information', {'fields': ['catalog_number']}),
    # ]
    list_display = ('subject', 'catalog_number')
    #list_display = ('question_text', 'pub_date', 'was_published_recently')
    #list_filter = ['pub_date']
    #search_fields = ['question_text']
admin.site.register(Class, ClassAdmin)

class ProfileAdmin(admin.ModelAdmin):
    display_list = ('user', 'courses', 'friends')
admin.site.register(Profile, ProfileAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    display_list = ('name', 'profile', 'courses')
admin.site.register(Schedule, ScheduleAdmin)

class Friend_RequestAdmin(admin.ModelAdmin):
    display_list = ('from_user', 'to_user')
admin.site.register(Friend_Request, Friend_RequestAdmin)

class CommentAdmin(admin.ModelAdmin):
    display_list = ('schedule', 'content', 'ups', 'downs')
admin.site.register(Comment, CommentAdmin)
# class All_classAdmin(admin.ModelAdmin):
#     display = ('name')
# admin.site.register(All_class, All_classAdmin)

# class FacilityAdmin(admin.ModelAdmin):
#     formfield_overrides = {
#         map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
#     }
# admin.site.register(Facility, FacilityAdmin)