from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtailsurveys.models import AbstractFormField, AbstractSurvey


class SurveyField(AbstractFormField):
    page = ParentalKey('SurveyPage', related_name='survey_form_fields')


class SurveyPage(AbstractSurvey):
    def get_context(self, request, *args, **kwargs):
        context = super(SurveyPage, self).get_context(request)
        context['greeting'] = "hello world"
        return context

SurveyPage.content_panels = [
    FieldPanel('title', classname="full title"),
    InlinePanel('survey_form_fields', label="Form fields"),
]
