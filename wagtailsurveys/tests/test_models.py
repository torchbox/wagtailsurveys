# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.test import TestCase

from wagtail.wagtailcore.models import Page
from wagtailsurveys.models import FormSubmission
from wagtailsurveys.tests.testapp.models import SurveyField
from wagtailsurveys.tests.utils import make_survey_page


class TestFormSubmission(TestCase):
    def setUp(self):
        # Create a survey page
        self.survey_page = make_survey_page()

    def test_get_survey(self):
        response = self.client.get('/let-us-know/')

        # Check response
        self.assertContains(response, """<label for="id_your-name">Your name</label>""")
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # check that variables defined in get_context are passed through to the template (#1429)
        self.assertContains(response, "<p>hello world</p>")

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
            'your-name': 'bob@example.com',
            'your-biography': 'hello world',
            'your-choices': {'foo': '', 'bar': '', 'baz': ''}
        })

        # Check response
        self.assertTemplateNotUsed(response, 'wagtailsurveys_tests/survey_page.html')
        self.assertTemplateUsed(response, 'wagtailsurveys_tests/survey_page_landing.html')

        # check that variables defined in get_context are passed through to the template (#1429)
        self.assertContains(response, "<p>hello world</p>")

        # Check that form submission was saved correctly
        survey_page = Page.objects.get(url_path='/home/let-us-know/')
        self.assertTrue(FormSubmission.objects.filter(page=survey_page, form_data__contains='hello world').exists())

    def test_post_unicode_characters(self):
        self.client.post('/let-us-know/', {
            'your-name': 'bob',
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
            'your-name': 'bob',
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
            'your-name': 'bob@example.com',
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