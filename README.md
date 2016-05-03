# wagtailsurveys

A module for Wagtail that provides ability to build polls and surveys.

## How to install

Install using pip:

```
pip install git+https://github.com/torchbox/wagtailsurveys.git
```

### Settings

In your settings file, add `wagtailsurveys` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'wagtailsurveys',
    # ...
]
```

## How to use

### The basics

To build polls or surveys you need to define two models within the `models.py` of one of your apps:
* Page model that extends `wagtailsurveys.models.AbstractSurvey`.
* Inline model for form fields that extends `wagtailsurveys.models.AbstractFormField`.

For example:
```python
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models


class SurveyPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]


class SurveyFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyPage, related_name='survey_form_fields')

```

`AbstractSurvey` expects `survey_form_fields` to be defined.
Any additional fields are treated as ordinary page content - note that `SurveyPage`
is responsible for serving both the form page itself and the landing page after submission,
so the model definition should include all necessary content fields for both of those views.

You now need to create two templates named `survey_page.html` and `survey_page_landing.html`
(where `survey_page` is the underscore-formatted version of the class name). `survey_page.html`
differs from a standard Wagtail template in that it is passed a variable `form`,
containing a Django `Form` object, in addition to the usual `page` variable.
A very basic template for the survey page would thus be:

```django
{% load wagtailcore_tags %}

<html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>
        <h1>{{ page.title }}</h1>

        <p>{{ self.intro|richtext }}</p>
        <form action="{% pageurl self %}" method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit">
        </form>
    </body>
</html>

```

`survey_page_landing.html` is a regular Wagtail template, displayed after the user makes a successful form submission.


### Customising

#### Custom `related_name` for form fields

If you want to change `related_name` for form fields
(by default `AbstractSurvey` expects `survey_form_fields` to be defined),
you will need to override `get_form_fields` method.
You can do this as shown below.

```python
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models


class SurveyPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('custom_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_form_fields(self):
        return self.custom_form_fields.all()


class SurveyFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyPage, related_name='custom_form_fields')
```

#### Custom form submission model

If you need to save additional data, you can use custom form submission model.
To do this, you need to:
* Define model that extends `wagtailsurveys.models.AbstractFormSubmission`.
* Override `get_submission_class` and `process_form_submission` methods in page model.

For example:
```python
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models


class SurveyWithCustomSubmissionPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_submission_class(self):
        return CustomFormSubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self, user=form.user
        )


class SurveyWithCustomSubmissionFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyWithCustomSubmissionPage, related_name='survey_form_fields')


class CustomFormSubmission(surveys_models.AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

#### Add custom data to CSV export

If you want to add custom data to CSV export, you will need to:
* Override `get_data_fields` method in page model.
* Override `get_data` in submission model.

The following example shows how to add a username to CSV export:

```python
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models


class SurveyWithCustomSubmissionPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_data_fields(self):
        data_fields = [
            ('username', 'Username'),
        ]
        data_fields += super(SurveyWithCustomSubmissionPage, self).get_data_fields()

        return data_fields

    def get_submission_class(self):
        return CustomFormSubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self, user=form.user
        )


class SurveyWithCustomSubmissionFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyWithCustomSubmissionPage, related_name='survey_form_fields')


class CustomFormSubmission(surveys_models.AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_data(self):
        form_data = super(CustomFormSubmission, self).get_data()
        form_data.update({
            'username': self.user.username,
        })

        return form_data
```

Note that this code also changes submissions list view.


#### How to check that submission already exists for a user

If you want to forbid users to take survey or poll twice,
you need to override `serve` method in page model.

For example:
```python
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.shortcuts import render
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models


class SurveyWithCustomSubmissionPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_submission_class(self):
        return CustomFormSubmission

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
    page = ParentalKey(SurveyWithCustomSubmissionPage, related_name='survey_form_fields')


class CustomFormSubmission(surveys_models.AbstractFormSubmission):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('page', 'user')
```

Now you need to create template like this:

```django
{% load wagtailcore_tags %}
<html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>
        <h1>{{ page.title }}</h1>

        {% if user.is_authenticated and user.is_active or request.is_preview %}
            {% if form %}
                <div>{{ self.intro|richtext }}</div>
                <form action="{% pageurl self %}" method="POST">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <input type="submit">
                </form>
            {% else %}
                <div>The survey has already been passed.</div>
            {% endif %}
        {% else %}
            <div>To take survey, you must to log in.</div>
        {% endif %}
    </body>
</html>
```

## How to run tests

To run tests you need to clone this repository:

    git clone https://github.com/torchbox/wagtailsurveys.git
    cd wagtailsurveys

With your preferred virtualenv activated, install testing dependencies:

    pip install -e .[testing] -U

Now you can run tests as shown below:

    python runtests.py