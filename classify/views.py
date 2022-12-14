
from email import message
from http.client import HTTPResponse
from ssl import AlertDescription
import requests
from django.contrib import messages
# Create your views here.
from email.policy import HTTP
from select import select
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Max

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect ,Http404

from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.shortcuts import redirect

from classify.models import Class, Dept, Profile, ProfileForm, Schedule, ScheduleForm, Friend_Request, Comment
# import logging
# logger = logging.getLogger(__name__)
from django.conf import settings
import json
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

def search(request):
    if 'q' in request.GET:
        message = 'You submitted: %r' % request.GET['q']
    else:
        message = 'You submitted nothing!'

    return HttpResponse(message)

# the user does not have to login in order to search or browse the courses
def index(request):
    isSearchError = False; # used to show an error if the user improperly searches
    typeOfError = '' # used to show the type of the error

    # Get the list of departments
    dept_results = {}
    response = requests.get('http://luthers-list.herokuapp.com/api/deptlist/')
    data = response.json()
    results = data
    Dept.objects.all().delete()
    for r in results:
        result_info = Dept(subject = r['subject'])
        result_info.save()
        dept_results = Dept.objects.all()

    deptlist = Dept.objects.all().order_by('subject')
    query_results = {}
    # deal with the condition when user trys to add a course to the shoppingcart
    # if the user clicks on star, then do not clear the Class database 
    if request.method == "POST" and request.POST.get("course_pk"):
        # if the user wants to use the shoppingcart but did not login, redirect to login page
        if(not request.user.is_authenticated):
            return redirect("/accounts/google/login/")
        course_id = request.POST.get("course_pk")
        course = Class.objects.get(course_number = course_id)
        request.user.profile.courses.add(course)
        message_display = course.subject+course.catalog_number+"("+course.course_section+")"
        messages.success(request,(f'{message_display} has been added to your Favorited Classes.'))
        # after user just used the shoppingcart, fetch the last department viewed by the user
        sq = request.session['sq']
        num_sq = request.session['num_sq']
        
    else:
    # if not the case when the user trys to add a course to the shoppingcart, reload the page with new department database

        # first check if there is valid value for the search bar
        sq = request.POST.get('dpt_search', None)
        num_sq = request.POST.get('num_search', None)
        if(sq or num_sq):
            if(sq):
                sq = str.upper(str(sq))
            if(num_sq):
                num_sq = str(num_sq)

            #  check searching bar to see if it is a valid search
            # early error handling - these will prevent results from being returned if search is not valid
            if sq and sq!='' and (len(sq) > 4 or 0 < len(sq) < 2):
                isSearchError = True
                typeOfError = 'Your department code is invalid. Please enter a valid code (e.g. "APMA").'
            elif num_sq and num_sq!='' and (not num_sq.isnumeric()):
                isSearchError = True
                typeOfError = 'Your catalog number is invalid. Please enter a valid number (e.g. "3240").'

        # immediately returns some errors earlier, if there is no chance of a result being returned
        if isSearchError:
            messages.error(request, typeOfError)
            return redirect('/classify')

        # first check if the user pushes the button of a dept name
        if(not sq and not num_sq):
            for dept in dept_results:
                dept_string = dept.subject
                if not sq:
                    sq = request.POST.get(dept_string, None)
            if(sq):
                sq = str.upper(str(sq))

        

        # if the subject searched is not searched before, then add course classes to the database
        if 'stored_subject' not in request.session:
            request.session['stored_subject']=[]

        # if the department is first time viewed, add that department to the session and store the course data for that department
        if sq is not None and sq != '' and sq not in request.session['stored_subject']:
            request.session['stored_subject'].append(sq)
            response = requests.get('http://luthers-list.herokuapp.com/api/dept/%s/' % sq)
            data = response.json()
            results = data

            for r in results:
                # convert the start_time and end_time into readable manner
                if (r["meetings"]):
                    start_time = r["meetings"][0]["start_time"][0:5]
                    end_time = r["meetings"][0]["end_time"][0:5]
                    meeting_days = r['meetings'][0]['days']
                    facility_description = r['meetings'][0]['facility_description']
                else:
                    start_time=''
                    end_time=''
                    meeting_days=''
                    facility_description=''
                if(start_time!=""):
                    if(float(start_time)<10):
                        start_time = start_time[1:]
                    if(float(start_time)>=12):
                        if(float(start_time)>=13):
                            start_time = str("{:.2f}".format(float(start_time)-12))+"pm"
                        else:
                            start_time=start_time+"pm"
                    else:
                        start_time = start_time+"am"
                
                if(end_time!=""):
                    if(float(end_time)<10):
                        end_time = end_time[1:]
                    if(float(end_time)>=12):
                        if(float(end_time)>=13):
                            end_time = str("{:.2f}".format(float(end_time)-12))+"pm"
                        else:
                            end_time=end_time+"pm"
                    else:
                        end_time = end_time+"am"
                
                result_info = Class(
                    instructor_name = r['instructor']['name'],
                    instructor_email = r['instructor']['email'],
                    course_number = r['course_number'],
                    semester_code = r['semester_code'],
                    course_section = r['course_section'],
                    subject = r['subject'],
                    catalog_number = r['catalog_number'],
                    description = r['description'],
                    units = r['units'],
                    component = r['component'],
                    class_capacity = r['class_capacity'],
                    wait_list = r['wait_list'],
                    wait_cap = r['wait_cap'],
                    enrollment_total = r['enrollment_total'],
                    enrollment_available = r['enrollment_available'],
                    topic = r['topic'],
                    meetings_days = meeting_days,
                    meetings_start_time = start_time,
                    meetings_end_time = end_time,
                    facility_description = facility_description,
            )
                result_info.save()
        # remove potential duplicates for classes in the database
        for duplicates in Class.objects.values("course_number").annotate(
                records=Count("course_number")
            ).filter(records__gt=1):
            for tag in Class.objects.filter(course_number=duplicates["course_number"])[1:]:
                tag.delete()
        # this session stores the department and the catalog_number of the last view so that the user will be back to the last page after add a course to shoppingcart
        request.session['sq']=sq
        request.session['num_sq']=num_sq

    # if there is a valid search, return a specific results with subject and catalog to the user, else just return the subject
    
    if(sq and num_sq):
        query_results = Class.objects.filter(subject=sq, catalog_number=num_sq).order_by('id')
        if(not query_results):
            messages.error(request, 'No results found.')
            return redirect('/classify')
    elif(sq):
        query_results = Class.objects.filter(subject=sq).order_by('id')
        if(not query_results):
            messages.error(request, 'No results found.')
            return redirect('/classify')
    elif(num_sq):
        query_results = Class.objects.filter(catalog_number=num_sq).order_by('subject')
        if(not query_results):
            messages.error(request, 'No results found.')
            return redirect('/classify')
        
    return render(request, 'classify/index.html', {
        # map feature
        "google_api_key": settings.GOOGLE_API_KEY,
        "query_results": query_results,
        'deptlist': deptlist,
    })

def user(request):
    if (request.user.is_authenticated):
        schedule = ScheduleForm(instance=request.user.profile.schedule)
        profile = ProfileForm(instance=request.user.profile)

        # if the user tries to delete a course from the shopping cart, fetch the course by its course_number and delete it from user's shopping cart.
        if request.method == 'POST' and request.POST.get('delete_course'):
            CourseNumToDelete = request.POST.get('delete_course')

            # User remove instead of delete to remove a course from the user profile without deleting the course itself in the Class model
            CourseToDelete = request.user.profile.courses.all().get(course_number=CourseNumToDelete)
            # remove the course from both shoppingcart and the schedule
            request.user.profile.courses.remove(CourseToDelete)
            request.user.profile.schedule.courses.remove(CourseToDelete)
            messages.success(request, (f'{CourseToDelete.subject}{CourseToDelete.catalog_number} has been deleted from your Favorited Classes and your Schedule.'))
            # CourseToDelete.save()
            return redirect('/user')

        conflict = False
        # if the user adds a class to the schedule, add that class to the user's schedule model
        if request.method == 'POST' and request.POST.get('add_to_schedule'):
            CourseNumToAdd = request.POST.get('add_to_schedule')
            CourseToAdd = request.user.profile.courses.all().get(course_number=CourseNumToAdd)
            # if a course in the schedule conflicts with this one, it cannot be added
            # if this course already exists in the schedule at a different time, it cannot be added (i.e. cannot enroll in two sections)
            meetings_days = CourseToAdd.meetings_days
            meetings_start_time = CourseToAdd.meetings_start_time
            for course in request.user.profile.schedule.courses.all():
                # no same course
                if((CourseToAdd.subject == course.subject) and (CourseToAdd.catalog_number == course.catalog_number) and (CourseToAdd.component == course.component)):
                    messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} is already in your Schedule.'))
                    conflict = True
                    break
                # no same time
                else:
                    if((CourseToAdd.meetings_days != "-") and (course.meetings_days != "-")):
                        conflict = conflict_check(CourseToAdd, course)
                        if(conflict):
                            messages.error(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} has a time conflict with {course.subject}{course.catalog_number} in your Schedule.'))
                            break
            if not conflict:
                messages.success(request, (f'{CourseToAdd.subject}{CourseToAdd.catalog_number} added to your schedule'))
                request.user.profile.schedule.courses.add(CourseToAdd)        
        return render(request, 'classify/user.html', {"user":request.user, "profile":profile, "schedule":schedule, "conflict":conflict})
    else:
        return redirect("/accounts/google/login/")

# determine if two courses conflict
def conflict_check(course_one, course_two):
    meetings_days_one = course_one.meetings_days
    meetings_days_two = course_two.meetings_days
    conflict = False
    if(("Mo" in meetings_days_one) and ("Mo" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Tu" in meetings_days_one) and ("Tu" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("We" in meetings_days_one) and ("We" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Th" in meetings_days_one) and ("Th" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    if(("Fr" in meetings_days_one) and ("Fr" in meetings_days_two)):
        conflict = conflict or conflict_on_day(course_one, course_two)
    return conflict

# determine if two courses on the same day conflict
def conflict_on_day(course_one, course_two):
    #Get strings of start and end times
    meetings_start_one = course_one.meetings_start_time
    meetings_end_one = course_one.meetings_end_time
    meetings_start_two = course_two.meetings_start_time
    meetings_end_two = course_two.meetings_end_time

    integer_start_one = time_to_float(meetings_start_one)
    integer_end_one = time_to_float(meetings_end_one)
    integer_start_two = time_to_float(meetings_start_two)
    integer_end_two = time_to_float(meetings_end_two)

    #Conflict if start_two <= end_one <= end_two (I.e. class one ends during class two)
    if(integer_end_one >= integer_start_two and integer_end_one <= integer_end_two):
        return True
    #Conflict if start_one <= end_two <= end_one (I.e. class two ends during class one)
    if(integer_end_two >= integer_start_one and integer_end_two <= integer_end_one):
        return True
    return False

# Turns a string of format 11.00am into a float 11.00 or 1.00 pm into 13
def time_to_float(time_string):
    time_float = float(time_string[:len(time_string)-2])
    #Add 12 if PM, but not if 12 PM
    if("pm" in time_string and "12" not in time_string[:2]):
        time_float += 12
    #Subtract 12 if 12 AM. Possibly an astronomy lab could happen near midnight, still need comparison
    if("am" in time_string and "12" in time_string[:2]):
        time_float -= 12
    return time_float

# Get the time_float of a course start time
def get_time_float_start(course):
    return time_to_float(course.meetings_start_time)

# show the schedule of the current user
def schedule(request):
    if (request.user.is_authenticated):
        # if the user tries to delete a course from the schedule, fetch the course by its course_number and delete it from user's schedule.
        if request.method == 'POST' and request.POST.get('delete_course'):
            CourseNumToDelete = request.POST.get('delete_course')
            CourseToDelete = request.user.profile.schedule.courses.all().get(course_number=CourseNumToDelete)
            # using remove for manytomany relationship can remove the object from somewhere without deleting itself
            request.user.profile.schedule.courses.remove(CourseToDelete)
            messages.success(request, (f'{CourseToDelete.subject}{CourseToDelete.catalog_number} has been deleted from your Schedule.'))
            return redirect('/user/schedule')
        
        # Put the courses into the correct days, so that the html file can access them
        monday_courses = []
        tuesday_courses = []
        wednesday_courses = []
        thursday_courses = []
        friday_courses = []
        other_courses = []
        for course in request.user.profile.schedule.courses.all():
            if "Mo" in course.meetings_days:
                monday_courses.append(course)
            if "Tu" in course.meetings_days:
                tuesday_courses.append(course)
            if "We" in course.meetings_days:
                wednesday_courses.append(course)
            if "Th" in course.meetings_days:
                thursday_courses.append(course)
            if "Fr" in course.meetings_days:
                friday_courses.append(course)
            if "Mo" not in course.meetings_days:
                if "Tu" not in course.meetings_days:
                    if "We" not in course.meetings_days:
                        if "Th" not in course.meetings_days:
                            if "Fr" not in course.meetings_days:
                                other_courses.append(course)

        # Sort the list of days
        monday_courses.sort(key=get_time_float_start)
        tuesday_courses.sort(key=get_time_float_start)
        wednesday_courses.sort(key=get_time_float_start)
        thursday_courses.sort(key=get_time_float_start)
        friday_courses.sort(key=get_time_float_start)
        # Don't sort other_courses I guess?

        # get all comments that belong to my schedule
        comments = Comment.objects.filter(schedule=request.user.profile.schedule)

        # if the user votes up, then the ups for that comment +1, and then add the current user to the voted_user list of the comment to prevent second vote
        if request.POST.get('comment_up') or request.POST.get('comment_down'):
            if(request.POST.get('comment_up')):
                comment_up = request.POST.get('comment_up')
                comment = Comment.objects.get(id=comment_up)
                if request.user not in comment.voted_users.all():
                    comment.ups+=1
            elif(request.POST.get('comment_down')):
                comment_down = request.POST.get('comment_down')
                comment = Comment.objects.get(id=comment_down)
                if request.user not in comment.voted_users.all():
                    comment.downs+=1            
            if request.user not in comment.voted_users.all():
                comment.voted_users.add(request.user)
            comment.save()

        # similar code to the above for if a user upvotes or downvotes the schedule as a whole
        if request.POST.get('schedule_up') or request.POST.get('schedule_down'):
            if(request.POST.get('schedule_up')):
                schedule_up = request.POST.get('schedule_up')
                schedule = request.user.profile.schedule
                if request.user not in schedule.voted_users.all():
                    schedule.ups+=1
            elif(request.POST.get('schedule_down')):
                schedule_down = request.POST.get('schedule_down')
                schedule = request.user.profile.schedule
                if request.user not in schedule.voted_users.all():
                    schedule.downs+=1            
            if request.user not in schedule.voted_users.all():
                schedule.voted_users.add(request.user)
            schedule.save()

        return render(request, 'classify/schedule.html', {"user":request.user, "schedule": request.user.profile.schedule, 'comments':comments, "monday_courses": monday_courses, "tuesday_courses": tuesday_courses, "wednesday_courses": wednesday_courses, "thursday_courses": thursday_courses, "friday_courses": friday_courses, "other_courses": other_courses})
    else:
        return redirect("/accounts/google/login/")

# implement a map feature where the user can check the position of a course on google map.
# Handles directions from Google by implementing googleapis jason map data

def Directions(*args, **kwargs):

    current_position = kwargs.get("current_position")
    target_position = kwargs.get("target_position")

    find_current_position_id = requests.get(
        'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?',
        params={
            'input': current_position,
            'inputtype' : 'textquery',
            "key": settings.GOOGLE_API_KEY
        })
    if find_current_position_id.json()["status"] == "OK":
        current_position_id = find_current_position_id.json()["candidates"][0]["place_id"]

    find_target_position_id = requests.get(
        'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?',
        params={
            'input': target_position,
            'inputtype' : 'textquery',
            "key": settings.GOOGLE_API_KEY
        })
    if find_target_position_id.json()["status"] == "OK":
        target_position_id = find_target_position_id.json()["candidates"][0]["place_id"]

    result = requests.get(
        'https://maps.googleapis.com/maps/api/directions/json?',
         params={
         'origin': 'place_id:'+current_position_id,
         'destination': 'place_id:'+target_position_id,
         'mode' : 'walking',
         "key": settings.GOOGLE_API_KEY
         })

    directions = result.json()

    if directions["status"] == "OK":

        route = directions["routes"][0]["legs"][0]
        origin = current_position
        destination = target_position
        distance = route["distance"]["text"]
        duration = route["duration"]["text"]

        # steps = [
        #     [
        #         s["distance"]["text"],
        #         s["duration"]["text"],
        #         s["html_instructions"],

        #     ]
        #     for s in route["steps"]]

    return {
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "duration": duration,
        # "steps": steps
        }

# define the map
def map(request):
    if(request.GET.get("current_position")):
        current_position = request.GET.get("current_position")
        target_position = request.GET.get("target_position")
        directions = Directions(
            current_position= current_position,
            target_position=target_position,
            )

        context = {
        "google_api_key": settings.GOOGLE_API_KEY,
        "origin": current_position,
        "destination": target_position,
        "directions": directions,

        }
        return render(request, 'classify/map.html', context)   
    
    messages.warning(request, "You must choose a course to show its location.")
    return redirect ("/classify")  

# define the user friend request
def send_friend_request(request, userID):
    from_user = request.user
    to_user = User.objects.get(id=userID)
    if(to_user in from_user.profile.friends.all()):
        messages.error(request, 'You are already friends.')
        return redirect('/classify/user/friend_search')
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        messages.success(request, f'A friend request to {to_user} has been sent.')
    else:
        messages.warning(request, f'A friend request to {to_user} has already been sent.')
    return redirect('/classify/user/friend_search')

# accept the user friend request
def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    # if the current user is the right target and both sides are not friends for now, then add them to friends
    if friend_request.to_user == request.user and friend_request.from_user not in request.user.profile.friends.all():
        friend_request.to_user.profile.friends.add(friend_request.from_user)
        friend_request.from_user.profile.friends.add(friend_request.to_user)
        # delete friend request alfter adding friends
        friend_request.delete()
        messages.success(request, f'Friend request accepted.')
    else:
        friend_request.delete()
        messages.error(request, f'You guys are already friends!')
    return redirect('/classify/user/friends')

# decline the user friend request
def decline_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    # simply delete the friend request
    friend_request.delete()
    messages.success(request, f'Friend request declined.')
    return redirect('/classify/user/friends')
    
# open friend search page
def friend_search(request):
    if (request.user.is_authenticated):
        search = request.POST.get('friend_search')
        if(search!=''):        
            return render(request, 'classify/friend_search.html', {'user':request.user, 'users':User.objects.filter(username=search)})
        else:
            return render(request, 'classify/friend_search.html', {'user':request.user})
    else:
        return redirect("/accounts/google/login/")

# page for display friends and their schedules
def friends(request):
    if (request.user.is_authenticated):
        # if a request of friends delete
        if request.method == 'POST' and request.POST.get('delete_friend'):
            FriendIDToDelete = request.POST.get('delete_friend')
            FriendToDelete = User.objects.get(id=FriendIDToDelete)        
            # delete the friend from user side
            request.user.profile.friends.remove(FriendToDelete)
            # delete the user from his/her friends' side
            FriendToDelete.profile.friends.remove(request.user)
            messages.success(request, (f'You have removed {FriendToDelete} from your Friends list.'))
            return redirect('/classify/user/friends')

        # process if the user check the schedule of a friend or the user comments
        if request.method == 'POST' and (request.POST.get('check_friend_schedule') or request.POST.get('friend_id')):
            # get user id from different situations
            if request.POST.get('check_friend_schedule'):
                friend_id = request.POST.get('check_friend_schedule')
            else:
                friend_id = request.POST.get('friend_id')
            friend = User.objects.get(id=friend_id)
            friend_schedule=friend.profile.schedule

            # if the user comments, create a new comment object and add that to the friend's schedule
            if request.POST.get('comment'):
                content = request.POST.get('comment')
                comment = Comment(
                    schedule = friend_schedule,
                    content = content,
                    pub_date = timezone.now(),
                )
                comment.save()
                
            # get all comments of a friend's schedule
            comments = Comment.objects.filter(schedule=friend_schedule)

            # if the user votes up, then the ups for that comment +1, and then add the current user to the voted_user list of the comment to prevent second vote
            if request.POST.get('comment_up') or request.POST.get('comment_down'):
                if(request.POST.get('comment_up')):
                    comment_up = request.POST.get('comment_up')
                    comment = Comment.objects.get(id=comment_up)
                    if request.user not in comment.voted_users.all():
                        comment.ups+=1
                elif(request.POST.get('comment_down')):
                    comment_down = request.POST.get('comment_down')
                    comment = Comment.objects.get(id=comment_down)
                    if request.user not in comment.voted_users.all():
                        comment.downs+=1            
                if request.user not in comment.voted_users.all():
                    comment.voted_users.add(request.user)
                comment.save()

            # remove potential duplicates for comments in the database
            for duplicates in comments.values("content").annotate(records=Count("content")).filter(records__gt=1):
                for tag in comments.filter(content=duplicates["content"])[1:]:
                    tag.delete()
            # order the comments by its publishing time
            comments=comments.order_by('pub_date')

            # similar code to the above for if a user upvotes or downvotes the schedule as a whole
            if request.POST.get('schedule_up') or request.POST.get('schedule_down'):
                if(request.POST.get('schedule_up')):
                    schedule_up = request.POST.get('schedule_up')
                    if request.user not in friend_schedule.voted_users.all():
                        friend_schedule.ups+=1
                elif(request.POST.get('schedule_down')):
                    schedule_down = request.POST.get('schedule_down')
                    if request.user not in friend_schedule.voted_users.all():
                        friend_schedule.downs+=1            
                if request.user not in friend_schedule.voted_users.all():
                    friend_schedule.voted_users.add(request.user)
                friend_schedule.save()

            # Put the courses into the correct days, so that the html file can access them
            monday_courses = []
            tuesday_courses = []
            wednesday_courses = []
            thursday_courses = []
            friday_courses = []
            other_courses = []
            for course in friend_schedule.courses.all():
                if "Mo" in course.meetings_days:
                    monday_courses.append(course)
                if "Tu" in course.meetings_days:
                    tuesday_courses.append(course)
                if "We" in course.meetings_days:
                    wednesday_courses.append(course)
                if "Th" in course.meetings_days:
                    thursday_courses.append(course)
                if "Fr" in course.meetings_days:
                    friday_courses.append(course)
                if "Mo" not in course.meetings_days:
                    if "Tu" not in course.meetings_days:
                        if "We" not in course.meetings_days:
                            if "Th" not in course.meetings_days:
                                if "Fr" not in course.meetings_days:
                                    other_courses.append(course)
            # Sort the list of days
            monday_courses.sort(key=get_time_float_start)
            tuesday_courses.sort(key=get_time_float_start)
            wednesday_courses.sort(key=get_time_float_start)
            thursday_courses.sort(key=get_time_float_start)
            friday_courses.sort(key=get_time_float_start)
            return render(request, 'classify/friends.html', {'user':request.user, 'friend':friend, 'comments':comments, 'friend_request': Friend_Request.objects.filter(to_user=request.user), 'friend_schedule':friend_schedule, "monday_courses": monday_courses, "tuesday_courses": tuesday_courses, "wednesday_courses": wednesday_courses, "thursday_courses": thursday_courses, "friday_courses": friday_courses, "other_courses": other_courses})
        else:
            return render(request, 'classify/friends.html', {'user':request.user, 'friend_request': Friend_Request.objects.filter(to_user=request.user)})
    else:
        return redirect("/accounts/google/login/")