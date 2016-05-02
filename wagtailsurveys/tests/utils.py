from __future__ import unicode_literals

from wagtail.wagtailcore.models import Page
from wagtailsurveys.tests.testapp.models import (
    SurveyPage, SurveyField,
    SurveyWithCustomSubmissionPage, SurveyWithCustomSubmissionFormField
)


def make_survey_page(**kwargs):
    kwargs.setdefault('title', "Let us know!")
    kwargs.setdefault('slug', "let-us-know")

    home_page = Page.objects.get(url_path='/home/')
    survey_page = home_page.add_child(instance=SurveyPage(**kwargs))

    SurveyField.objects.create(
        page=survey_page,
        sort_order=1,
        label="Your name",
        field_type='singleline',
        required=True,
    )
    SurveyField.objects.create(
        page=survey_page,
        sort_order=2,
        label="Your biography",
        field_type='multiline',
        required=True,
    )
    SurveyField.objects.create(
        page=survey_page,
        sort_order=3,
        label="Your choices",
        field_type='checkboxes',
        required=False,
        choices='foo,bar,baz',
    )

    return survey_page


def make_survey_page_with_custom_submission(**kwargs):
    kwargs.setdefault('title', "Don't touch this survey!")
    kwargs.setdefault('slug', "dont-touch-this-survey")

    home_page = Page.objects.get(url_path='/home/')
    survey_page = home_page.add_child(instance=SurveyWithCustomSubmissionPage(**kwargs))

    SurveyWithCustomSubmissionFormField.objects.create(
        page=survey_page,
        sort_order=1,
        label="Your name",
        field_type='singleline',
        required=True,
    )
    SurveyWithCustomSubmissionFormField.objects.create(
        page=survey_page,
        sort_order=2,
        label="Your biography",
        field_type='multiline',
        required=True,
    )
    SurveyWithCustomSubmissionFormField.objects.create(
        page=survey_page,
        sort_order=3,
        label="Your choices",
        field_type='checkboxes',
        required=False,
        choices='foo,bar,baz',
    )

    return survey_page
