from __future__ import absolute_import, unicode_literals

import json
import re

from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.shortcuts import render
from django.utils.six import text_type
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from unidecode import unidecode

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page, Orderable, UserPagePermissionsProxy, get_page_models

from wagtailsurveys.forms import FormBuilder


@python_2_unicode_compatible
class AbstractFormSubmission(models.Model):
    """Data for a survey submission."""

    form_data = models.TextField()
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='+')

    created_at = models.DateTimeField(verbose_name=_('submit time'), auto_now_add=True)

    def get_data(self):
        return json.loads(self.form_data)

    def __str__(self):
        return self.form_data

    class Meta:
        abstract = True
        verbose_name = _('form submission')


class FormSubmission(AbstractFormSubmission):
    pass


class AbstractFormField(Orderable):
    """
    Database Fields required for building a Django Form field.
    """

    FORM_FIELD_CHOICES = (
        ('singleline', _('Single line text')),
        ('multiline', _('Multi-line text')),
        ('email', _('Email')),
        ('number', _('Number')),
        ('url', _('URL')),
        ('checkbox', _('Checkbox')),
        ('checkboxes', _('Checkboxes')),
        ('dropdown', _('Drop down')),
        ('radio', _('Radio buttons')),
        ('date', _('Date')),
        ('datetime', _('Date/time')),
    )

    label = models.CharField(
        verbose_name=_('label'),
        max_length=255,
        help_text=_('The label of the form field')
    )
    field_type = models.CharField(verbose_name=_('field type'), max_length=16, choices=FORM_FIELD_CHOICES)
    required = models.BooleanField(verbose_name=_('required'), default=True)
    choices = models.CharField(
        verbose_name=_('choices'),
        max_length=512,
        blank=True,
        help_text=_('Comma separated list of choices. Only applicable in checkboxes, radio and dropdown.')
    )
    default_value = models.CharField(
        verbose_name=_('default value'),
        max_length=255,
        blank=True,
        help_text=_('Default value. Comma separated values supported for checkboxes.')
    )
    help_text = models.CharField(verbose_name=_('help text'), max_length=255, blank=True)

    @property
    def clean_name(self):
        # unidecode will return an ascii string while slugify wants a
        # unicode string on the other hand, slugify returns a safe-string
        # which will be converted to a normal str
        return str(slugify(text_type(unidecode(self.label))))

    panels = [
        FieldPanel('label'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('choices', classname="formbuilder-choices"),
        FieldPanel('default_value', classname="formbuilder-default"),
    ]

    class Meta:
        abstract = True
        ordering = ['sort_order']


_FORM_CONTENT_TYPES = None


def get_survey_types():
    global _FORM_CONTENT_TYPES
    if _FORM_CONTENT_TYPES is None:
        form_models = [
            model for model in get_page_models()
            if issubclass(model, AbstractSurvey)
        ]

        _FORM_CONTENT_TYPES = list(
            ContentType.objects.get_for_models(*form_models).values()
        )
    return _FORM_CONTENT_TYPES


def get_surveys_for_user(user):
    """
    Return a queryset of form pages that this user is allowed to access the submissions for
    """
    editable_pages = UserPagePermissionsProxy(user).editable_pages()
    return editable_pages.filter(content_type__in=get_survey_types())


class AbstractSurvey(Page):
    """
    A Form Page. Pages implementing a survey form should inherit from it
    """

    HTML_EXTENSION_RE = re.compile(r"(.*)\.html")

    form_builder = FormBuilder

    def __init__(self, *args, **kwargs):
        super(AbstractSurvey, self).__init__(*args, **kwargs)
        if not hasattr(self, 'landing_page_template'):
            template_wo_ext = re.match(self.HTML_EXTENSION_RE, self.template).group(1)
            self.landing_page_template = template_wo_ext + '_landing.html'

    class Meta:
        abstract = True

    def get_form_class(self):
        form_builder = self.form_builder(self.form_fields.all())
        return form_builder.get_form_class()

    def get_form_parameters(self):
        return {}

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form_params.update(kwargs)

        return form_class(*args, **form_params)

    def get_submission_class(self):
        return FormSubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
        )

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.get_form(request.POST)

            if form.is_valid():
                self.process_form_submission(form)

                # render the landing_page
                # TODO: It is much better to redirect to it
                return render(
                    request,
                    self.landing_page_template,
                    self.get_context(request)
                )
        else:
            form = self.get_form()

        context = self.get_context(request)
        context['form'] = form
        return render(
            request,
            self.template,
            context
        )

    preview_modes = [
        ('form', 'Form'),
        ('landing', 'Landing page'),
    ]

    def serve_preview(self, request, mode):
        if mode == 'landing':
            return render(
                request,
                self.landing_page_template,
                self.get_context(request)
            )
        else:
            return super(AbstractSurvey, self).serve_preview(request, mode)
