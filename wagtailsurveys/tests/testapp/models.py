from __future__ import unicode_literals

import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.shortcuts import render
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtailsurveys import models as surveys_models


class SurveyPage(surveys_models.AbstractSurvey):
    def get_context(self, request, *args, **kwargs):
        context = super(SurveyPage, self).get_context(request)
        context['greeting'] = "hello world"
        return context

    content_panels = [
        FieldPanel('title', classname="full title"),
        InlinePanel('survey_form_fields', label="Form fields"),
    ]


class SurveyField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyPage, related_name='survey_form_fields')


class SurveyWithCustomSubmissionPage(surveys_models.AbstractSurvey):
    """
    This Survey page:
        * Have custom submission model
        * Have custom related_name (see `SurveyWithCustomSubmissionFormField.page`)
        * Saves reference to a user
        * Doesn't render html form, if submission for current user is present
    """

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('custom_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_form_fields(self):
        return self.custom_form_fields.all()

    def get_data_fields(self):
        data_fields = [
            ('username', 'Username'),
        ]
        data_fields += super(SurveyWithCustomSubmissionPage, self).get_data_fields()

        return data_fields

    def get_submission_class(self):
        return CustomSubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self, user=form.user
        )

    def serve(self, request, *args, **kwargs):
        if self.get_submission_class().objects.filter(page=self, user__pk=request.user.pk).exists():
            return render(
                request,
                self.template,
                self.get_context(request)
            )

        return super(SurveyWithCustomSubmissionPage, self).serve(request, *args, **kwargs)


class SurveyWithCustomSubmissionFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyWithCustomSubmissionPage, related_name='custom_form_fields')


class CustomSubmission(surveys_models.AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_data(self):
        form_data = super(CustomSubmission, self).get_data()
        form_data.update({
            'username': self.user.username,
        })

        return form_data
