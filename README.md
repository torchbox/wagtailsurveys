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

`AbstractSurvey` expects `survey_form_fields` to be defined. Any additional fields are treated as ordinary page content - note that `SurveyPage` is responsible for serving both the form page itself and the landing page after submission, so the model definition should include all necessary content fields for both of those views.

You now need to create two templates named `survey_page.html` and `survey_page_landing.html` (where `survey_page` is the underscore-formatted version of the class name). `survey_page.html` differs from a standard Wagtail template in that it is passed a variable `form`, containing a Django `Form` object, in addition to the usual `page` variable. A very basic template for the form would thus be:

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

## How to run tests

To run tests you need to clone this repository:

    git clone https://github.com/torchbox/wagtailsurveys.git
    cd wagtailsurveys

With your preferred virtualenv activated, install testing dependencies:

    pip install -e .[testing] -U

Now you can run tests as shown below:

    python runtests.py