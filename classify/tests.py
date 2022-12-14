from django.test import TestCase
import unittest

from django.test import Client
from classify.models import Class, Dept, Profile, Schedule, ProfileForm, ScheduleForm, Comment
from django.urls import reverse
from django.contrib.auth import get_user_model 
from classify.views import conflict_check, get_time_float_start, time_to_float, conflict_on_day

# Create your tests here.
class TestLogin(TestCase):
    def login_successful(self):
        self.assertIs(True)

    def test_something(self):
        session = self.client.session
        session['somekey'] = 'test'
        session.save()
    
    # def test_language_using_header(self):
    #     response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='fr')
    #     self.assertEqual(response.content, b"Bienvenue sur mon site.")

    class SimpleTest(unittest.TestCase):
        def setUp(self):
            # Every test needs a client.
            self.client = Client()

        def test_details(self):
            # Issue a GET request.
            response = self.client.get('/customer/details/')

            # Check that the response is 200 OK.
            self.assertEqual(response.status_code, 200)

            # Check that the rendered context contains 5 customers.
            self.assertEqual(len(response.context['customers']), 5)

class TestSearching(TestCase):
    def setUp(self):
        Dept.objects.create(subject="FAKE")
        Class.objects.create(catalog_number = 1, instructor_name = "Bob", subject = "FAKE", description = "Fake description", units = 3, enrollment_available = 20, class_capacity = 100, wait_list = 0, wait_cap = 10, meetings_days = "MoWe", meetings_start_time="17.00.00.000000-05:00", 
        meetings_end_time="18.15.00.000000-05:00", facility_description="Olsson Hall 009")

    def test_department(self):
        fake_dept = Dept.objects.get(subject="FAKE")
        self.assertEqual("FAKE", fake_dept.subject)

    def test_class_subject(self):
        fake_class = Class.objects.get(subject="FAKE")
        self.assertEqual("FAKE", fake_class.subject)

    def test_class_instructor(self):
        fake_class = Class.objects.get(subject="FAKE")
        self.assertEqual("Bob", fake_class.instructor_name)
    
    def test_class_description(self):
        fake_class = Class.objects.get(subject="FAKE")
        self.assertEqual("Fake description", fake_class.description)

    def test_class_units(self):
        fake_class = Class.objects.get(subject="FAKE")
        self.assertEqual('3', fake_class.units)
    def test_wait_list(self):
        fake_class = Class.objects.get(subject="FAKE")
        self.assertEqual(0, fake_class.wait_list)

class TestShoppingAndSchedule(TestCase):
    def setUp(self):
        Dept.objects.create(subject="FAKE")
        Dept.objects.create(subject="EKAF")
        Class.objects.create(subject = "FAKE", catalog_number = "1000", meetings_days = "MoWe", meetings_start_time = "12.00pm", meetings_end_time = "1.00pm", course_section = "001")
        Class.objects.create(subject = "FAKE", catalog_number = "1000", meetings_days = "TuTh", meetings_start_time = "9.00am", meetings_end_time = "10.00am", course_section = "002")
        Class.objects.create(subject = "FAKE", catalog_number = "2000", meetings_days = "MoWe", meetings_start_time = "11.00am", meetings_end_time = "12.00pm")
        Class.objects.create(subject = "EKAF", catalog_number = "1000", meetings_days = "TuTh", meetings_start_time = "11.00am", meetings_end_time = "1.00pm")
        Class.objects.create(subject = "EKAF", catalog_number = "2000", meetings_days = "TuTh", meetings_start_time = "12.00am", meetings_end_time = "1.00am")
        Class.objects.create(subject = "FAKE", catalog_number = "2500", meetings_days = "-", meetings_start_time = "-", meetings_end_time = "-")

        #Profile.objects.create()

    def test_conflict_none(self):
        class_one = Class.objects.get(subject = "FAKE", catalog_number = "1000", course_section = "001")
        class_two = Class.objects.get(subject = "EKAF", catalog_number = "1000")
        self.assertEqual(False, conflict_check(class_one, class_two))

    def test_conflict_around_noon(self):
        class_one = Class.objects.get(subject = "FAKE", catalog_number = "1000", course_section = "001")
        class_two = Class.objects.get(subject = "FAKE", catalog_number = "2000")
        self.assertEqual(True, conflict_check(class_one, class_two))

    def test_conflict_around_midnight(self):
        class_one = Class.objects.get(subject = "EKAF", catalog_number = "1000")
        class_two = Class.objects.get(subject = "EKAF", catalog_number = "2000")
        self.assertEqual(False, conflict_check(class_one, class_two))

    def test_conflict_normal(self):
        class_one = Class.objects.get(subject = "FAKE", catalog_number = "1000", course_section = "002")
        class_two = Class.objects.get(subject = "EKAF", catalog_number = "1000")
        self.assertEqual(False, conflict_check(class_one, class_two))

    def test_conflict_one_empty(self):
        class_one = Class.objects.get(subject = "FAKE", catalog_number = "1000", course_section = "002")
        class_two = Class.objects.get(subject = "FAKE", catalog_number = "2500")
        self.assertEqual(False, conflict_check(class_one, class_two))

    # Due to how the code is written, conflict_check will assume that the classes are not already the same class, dealt with elsewhere
    def test_conflict_both_empty(self):
        class_one = Class.objects.get(subject = "FAKE", catalog_number = "2500")
        class_two = Class.objects.get(subject = "FAKE", catalog_number = "2500")
        self.assertEqual(False, conflict_check(class_one, class_two))

class TestDept(TestCase):
    def test_dept_subject(self):
        Dept.objects.create(subject="TEST")
        fake_dept = Dept.objects.get(subject="TEST")
        self.assertEqual("TEST", fake_dept.subject)

class TestProfileForm(TestCase):
    def test_courses(self):
        form = ProfileForm(data={"courses":"A course here"})
        self.assertEqual(form.errors["courses"], ["Enter a list of values."])
class TestScheduleForm(TestCase):
    def test_schedule(self):
        form = ScheduleForm(data={"courses":"A course here"})
        self.assertEqual(form.errors["courses"], ["Enter a list of values."])
    def test_schedule_name(self):
        form = ScheduleForm(data={"name":"John Doe"})
        self.assertTrue(isinstance(form, ScheduleForm))
class ClassTest(TestCase):
    def create_class(self,
        instructor_name="John", 
        course_number=14839, 
        semester_code=1228, 
        course_section="001",
        subject="CS", 
        catalog_number="1010", 
        description="Introduction to Information Technology", 
        units="3", component="LEC", 
        class_capacity=75, 
        wait_list=0, 
        wait_cap=199, 
        enrollment_total=72, 
        enrollment_available=3, 
        topic="", 
        meetings_days="MoWe", 
        meetings_start_time="17.00.00.000000-05:00", 
        meetings_end_time="18.15.00.000000-05:00",
        facility_description="Olsson Hall 009"):
            return Class.objects.create(instructor_name=instructor_name, 
            course_number=course_number,
            semester_code = semester_code, 
            course_section=course_section, 
            subject=subject,
            catalog_number=catalog_number, 
            description=description, 
            units=units, 
            component=component, 
            class_capacity=class_capacity, 
            wait_list=wait_list, 
            wait_cap=wait_cap,
            enrollment_total=enrollment_total, 
            enrollment_available=enrollment_available, 
            topic=topic, 
            meetings_days=meetings_days, 
            meetings_start_time=meetings_start_time, 
            meetings_end_time=meetings_end_time, 
            facility_description=facility_description)
    def test_instructor_name(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("John", fake_class.instructor_name)
    def test_course_number(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(14839, fake_class.course_number)
    def test_semester_code(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(1228, fake_class.semester_code)
    def test_course_section(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual('001', fake_class.course_section)
    def test_catalog_number(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("1010", fake_class.catalog_number)
    def test_component(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("LEC", fake_class.component)
    def test_class_capacity(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(75, fake_class.class_capacity)
    def test_wait_cap(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(199, fake_class.wait_cap)
    def test_enrollment_total(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(72, fake_class.enrollment_total)
    def test_enrollment_available(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual(3, fake_class.enrollment_available)
    def test_topic(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("", fake_class.topic)
    def test_meetings_days(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("MoWe", fake_class.meetings_days)
    def test_meetings_start_time(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("17.00.00.000000-05:00", fake_class.meetings_start_time)
    def test_meetings_end_time(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("18.15.00.000000-05:00", fake_class.meetings_end_time)
    def test_facility_description(self):
        fake_class = self.create_class()
        self.assertTrue(isinstance(fake_class, Class))
        self.assertEqual("Olsson Hall 009", fake_class.facility_description)

class TestConflictCheck(TestCase):
    def create_class(self,
        instructor_name="John", 
        course_number=14839, 
        semester_code=1228, 
        course_section="001",
        subject="CS", 
        catalog_number="1010", 
        description="Introduction to Information Technology", 
        units="3", component="LEC", 
        class_capacity=75, 
        wait_list=0, 
        wait_cap=199, 
        enrollment_total=72, 
        enrollment_available=3, 
        topic="", 
        meetings_days="MoWe", 
        meetings_start_time="12.00pm", 
        meetings_end_time="2.00pm",
        facility_description="Olsson Hall 009"):
            return Class.objects.create(instructor_name=instructor_name, 
            course_number=course_number,
            semester_code = semester_code, 
            course_section=course_section, 
            subject=subject,
            catalog_number=catalog_number, 
            description=description, 
            units=units, 
            component=component, 
            class_capacity=class_capacity, 
            wait_list=wait_list, 
            wait_cap=wait_cap,
            enrollment_total=enrollment_total, 
            enrollment_available=enrollment_available, 
            topic=topic, 
            meetings_days=meetings_days,
            meetings_start_time = meetings_start_time, 
            meetings_end_time = meetings_end_time, 
            facility_description=facility_description)
    def test_conflict_check_no_conflict(self):
        fake_class_1 = self.create_class()
        fake_class_2 = self.create_class()
        fake_class_2.meetings_days = "TuTh"
        conflict_check(fake_class_1, fake_class_2)
        self.assertEqual(False, conflict_check(fake_class_1, fake_class_2))
    def test_conflict_check_yes_conflict(self):
        fake_class_1 = self.create_class()
        fake_class_2 = self.create_class()
        self.assertEqual(conflict_check(fake_class_1, fake_class_2), True)
    #testing the conflict_on_day function too 
    def test_conflict_on_day_false(self):
        fake_class_1 = self.create_class()
        fake_class_2 = self.create_class()
        fake_class_2.meetings_start_time = "11.00am"
        fake_class_2.meetings_end_time = "12.00pm"
        fake_class_1.meetings_start_time = "3.00pm"
        fake_class_1.meetings_end_time = "4.00pm"
        self.assertEqual(conflict_on_day(fake_class_1, fake_class_2), False)
    def test_conflict_on_day_true(self):
        fake_class_1 = self.create_class()
        fake_class_2 = self.create_class()
        fake_class_2.meetings_start_time = "11.00am"
        fake_class_2.meetings_end_time = "12.00pm"
        fake_class_1.meetings_start_time = "11.00am"
        fake_class_1.meetings_end_time = "12.00pm"
        self.assertEqual(True, conflict_on_day(fake_class_1, fake_class_2))
class TestFloat(TestCase):
    def create_class(self,
        meetings_start_time = "11.00am"):
            return Class.objects.create(meetings_start_time = meetings_start_time)
    def test_time_to_float_PM(self):
        time_string = "12.00pm"
        self.assertEqual(12, time_to_float(time_string))
    def test_time_to_float_AM(self):
        time_string = "12.00am"
        self.assertEqual(0, time_to_float(time_string))
    def test_time_to_float_non_12(self):
        time_string = "11.00am"
        self.assertEqual(11, time_to_float(time_string))
    def test_get_time_float_start(self):
        fake_class = self.create_class()
        self.assertEqual(11.00, get_time_float_start(fake_class))
