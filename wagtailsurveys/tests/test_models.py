# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import TestCase

from wagtail.tests.utils import WagtailTestUtils
from wagtail.wagtailcore.models import Page
from wagtailsurveys.models import FormSubmission
from wagtailsurveys.tests.testapp.models import SurveyField, CustomSubmission
from wagtailsurveys.tests import utils as tests_utils


class TestSurveyPageFormSubmission(TestCase):
    def setUp(self):
        # Create a survey page
        self.survey_page = tests_utils.make_survey_page()

    def test_get_survey(self):
        response = self.client.get('/let-us-know/')

        # Check response
        self.assertContains(response, """<label for="id_your-name">Your name</label>""", html=True)
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # check that variables defined in get_context are passed through to the template (#1429)
        self.assertContains(response, "<p>hello world</p>", html=True)

    def test_post_invalid_form(self):
        response = self.client.post('/let-us-know/', {
            'your-name': '',
            'your-biography': 'hello world',
            'your-choices': ''
        })

        # Check response
        self.assertContains(response, "This field is required.")
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

    def test_post_valid_form(self):
        response = self.client.post('/let-us-know/', {
            'your-name': 'Bob',
            'your-biography': 'hello world',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''}
        })

        # Check response
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # check that variables defined in get_context are passed through to the template (#1429)
        self.assertContains(response, "<p>hello world</p>", html=True)

        # Check that form submission was saved correctly
        survey_page = Page.objects.get(url_path='/home/let-us-know/')
        self.assertTrue(FormSubmission.objects.filter(page=survey_page, form_data__contains='hello world').exists())

    def test_post_unicode_characters(self):
        self.client.post('/let-us-know/', {
            'your-name': 'Bob',
            'your-biography': 'こんにちは、世界',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''}
        })

        # Check the form submission
        submission = FormSubmission.objects.get()
        submission_data = json.loads(submission.form_data)
        self.assertEqual(submission_data['your-biography'], 'こんにちは、世界')

    def test_post_number(self):
        # Add a number field to the page
        SurveyField.objects.create(
            page=self.survey_page,
            label="Your favourite number",
            field_type='number',
        )

        response = self.client.post('/let-us-know/', {
            'your-name': 'Bob',
            'your-biography': 'I\'m a boring person',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''},
            'your-favourite-number': '7.3',
        })

        # Check response
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # Check that form submission was saved correctly
        self.assertTrue(FormSubmission.objects.filter(page=self.survey_page, form_data__contains='7.3').exists())

    def test_post_multiple_values(self):
        response = self.client.post('/let-us-know/', {
            'your-name': 'Bob',
            'your-biography': 'hello world',
            'your-choices': {'foo': 'on', 'bar': 'on', 'baz': 'on'}
        })

        # Check response
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # Check that the three checkbox values were saved correctly
        survey_page = Page.objects.get(url_path='/home/let-us-know/')
        submission = FormSubmission.objects.filter(
            page=survey_page, form_data__contains='hello world'
        )
        self.assertIn("foo", submission[0].form_data)
        self.assertIn("bar", submission[0].form_data)
        self.assertIn("baz", submission[0].form_data)


class TestSurveyWithCustomSubmissionPageFormSubmission(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create a survey page
        self.survey_page = tests_utils.make_survey_page_with_custom_submission(**{
            'intro': '<p>Boring intro text</p>',
            'thank_you_text': '<p>Thank you for your patience!</p>',
        })

        self.user = self.login()

    def test_get_survey(self):
        response = self.client.get('/dont-touch-this-survey/')

        # Check response
        self.assertContains(response, """<label for="id_your-name">Your name</label>""", html=True)
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page_landing.html')
        self.assertNotContains(response, '<div>You must log in first.</div>', html=True)
        self.assertContains(response, '<p>Boring intro text</p>', html=True)

    def test_get_survey_with_anonymous_user(self):
        self.client.logout()
        response = self.client.get('/dont-touch-this-survey/')

        # Check response
        self.assertNotContains(response, """<label for="id_your-name">Your name</label>""", html=True)
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page_landing.html')
        self.assertContains(response, '<div>You must log in first.</div>', html=True)
        self.assertNotContains(response, '<p>Boring intro text</p>', html=True)

    def test_post_survey_twice(self):
        # First submission
        response = self.client.post('/dont-touch-this-survey/', {
            'your-name': 'Bob',
            'your-biography': 'hello world',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''}
        })

        # Check response
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page.html')
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page_landing.html')
        self.assertContains(response, '<p>Thank you for your patience!</p>', html=True)
        self.assertNotContains(response, '<div>The form is already filled.</div>', html=True)

        # Check that first form submission was saved correctly
        submissions_qs = CustomSubmission.objects.filter(user=self.user, page=self.survey_page)
        self.assertEqual(submissions_qs.count(), 1)
        self.assertTrue(submissions_qs.filter(form_data__contains='hello world').exists())

        # Second submission
        response = self.client.post('/dont-touch-this-survey/', {
            'your-name': 'Bob',
            'your-biography': 'hello cruel world',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''}
        })

        # Check response
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_with_custom_submission_page_landing.html')
        self.assertNotContains(response, '<p>Thank you for your patience!</p>', html=True)
        self.assertContains(response, '<div>The form is already filled.</div>', html=True)
        self.assertNotContains(response, '<div>You must log in first.</div>', html=True)
        self.assertNotContains(response, '<p>Boring intro text</p>', html=True)

        # Check that first submission exists and second submission wasn't saved
        submissions_qs = CustomSubmission.objects.filter(user=self.user, page=self.survey_page)
        self.assertEqual(submissions_qs.count(), 1)
        self.assertTrue(submissions_qs.filter(form_data__contains='hello world').exists())
        self.assertFalse(submissions_qs.filter(form_data__contains='hello cruel world').exists())
