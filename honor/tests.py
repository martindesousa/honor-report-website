from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from honor.models import Report, ResolutionStatus
from honor.forms import ReportForm
from .views import submitted_view
import os, boto3

#Citation: https://realpython.com/testing-in-django-part-1-best-practices-and-examples/

#Testing models
class ReportModelTestCase(TestCase):
    def test_valid_form(self):
        my_instance = Report.objects.create(nameOfOffender='Someone', description="Cheated on Exam")
        self.assertEqual(my_instance.nameOfOffender, 'Someone')
        self.assertEqual(my_instance.description, "Cheated on Exam")

    def test_new_report_status(self):
        my_instance = Report.objects.create(nameOfOffender='name')
        self.assertEqual(my_instance.status, ResolutionStatus.NEW)

    def test_new_report_status_name(self):
        my_instance = Report.objects.create(nameOfOffender='name')
        self.assertEqual(my_instance.get_status(), "NEW")

#Testing views
class MyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_home(self):
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)

    def test_view_submitReport(self):
        response = self.client.get("/report/")
        self.assertEqual(response.status_code, 200)
    
    def test_view_submitted(self):
        response = self.client.get("/submitted/")
        self.assertEqual(response.status_code, 200)

class MockReportTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.report = Report.objects.create(nameOfOffender='Test Offender', description='Test Description')

    def mock_report_submission(self):
        submission_data = {
            'nameOfOffender': 'Test Offender',
            'className': 'Test Class',
            'location': 'Test Location',
            'description': 'Test Description',
            'addInfo': 'Additional Info',
        }
        response = self.post('/submit_report/', submission_data)
        return response
    
    def mock_report_edit(self, report_id):
        edit_data = {
            'nameOfOffender': 'Updated Offender',
            'description': 'Updated Description',
        }
        response = self.post(f'/edit_report/{report_id}/', edit_data)
        return response

    def mock_report_deletion(self, report_id):
        response = self.post(f'/delete_report/{report_id}/')
        return response

    def mock_report_resolution(self, report_id):
        response = self.post(f'/resolve/{report_id}/')
        return response

    def test_delete_report(self):
        response = self.client.post(reverse('honor:delete_report', args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(Report.objects.all(), [])

class ReportResolutionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.report = Report.objects.create(nameOfOffender='Test Offender', description='Test Description')

    def test_resolve_report_view(self):
        response = self.client.get(reverse('honor:resolve', args=(self.report.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_resolve_report(self):
        response = self.client.post(reverse('honor:resolve', args=(self.report.pk,)))
        updated_report = Report.objects.get(pk=self.report.pk)
        self.assertEqual(updated_report.status, ResolutionStatus.RESOLVED)

#Testing forms
class MyFormTestCase(TestCase):
    def test_valid_form(self):
        form_data = {'nameOfOffender': 'Test', 'description': 'Testing'}
        form = ReportForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'nameOfOffender': '', 'description': ''}
        form = ReportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)