# Deprecated warning

Wagtailsurveys is now deprecated. It was ported into the primary Wagtail repository. Please use Wagtail's [Form builder](http://docs.wagtail.io/en/v2.4/reference/contrib/forms/index.html) instead - it [supports customisations](http://docs.wagtail.io/en/v2.4/reference/contrib/forms/customisation.html) described below.

# Wagtailsurveys

A module for Wagtail which provides the ability to build polls and surveys.

## How to install

Install using pip:

```
pip install wagtailsurveys
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
* A Page model that extends `wagtailsurveys.models.AbstractSurvey`.
* An Inline model for form fields that extends `wagtailsurveys.models.AbstractFormField`.

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
You also can change the landing template by specifying a `landing_page_template` attribute on your page model.

### Customising

#### Custom `related_name` for form fields

If you want to change `related_name` for form fields
(by default `AbstractSurvey` expects `survey_form_fields` to be defined),
you will need to override the `get_form_fields` method.
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

If you need to save additional data, you can use a custom form submission model.
To do this, you need to:
* Define a model that extends `wagtailsurveys.models.AbstractFormSubmission`.
* Override the `get_submission_class` and `process_form_submission` methods in your page model.

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

If you want to add custom data to the CSV export, you will need to:
* Override the `get_data_fields` method in page model.
* Override `get_data` in the submission model.

The following example shows how to add a username to the CSV export:

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

Note that this code also changes the submissions list view.

#### Check that a submission already exists for a user

If you want to prevent users from taking a survey or poll more than once,
you need to override the `serve` method in page model.

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

Now you will need to create a template like this:

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

#### Multi-step form

The following example shows how to create a multi-step form.

```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models

class SurveyWithPaginationPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_form_class_for_step(self, step):
        return self.form_builder(step.object_list).get_form_class()

    def serve(self, request, *args, **kwargs):
        """
        Implements simple a multi-step form.

        Stores each step into a session.
        When the last step was submitted correctly, saves whole form into a DB.
        """

        session_key_data = 'survey_data-%s' % self.pk
        is_last_step = False
        step_number = request.GET.get('p', 1)

        paginator = Paginator(self.get_form_fields(), per_page=1)
        try:
            step = paginator.page(step_number)
        except PageNotAnInteger:
            step = paginator.page(1)
        except EmptyPage:
            step = paginator.page(paginator.num_pages)
            is_last_step = True

        if request.method == 'POST':
            # The first step will be submitted with step_number == 2,
            # so we need to get a from from previous step
            # Edge case - submission of the last step
            prev_step = step if is_last_step else paginator.page(step.previous_page_number())

            # Create a form only for submitted step
            prev_form_class = self.get_form_class_for_step(prev_step)
            prev_form = prev_form_class(request.POST, page=self, user=request.user)
            if prev_form.is_valid():
                # If data for step is valid, update the session
                survey_data = request.session.get(session_key_data, {})
                survey_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = survey_data

                if prev_step.has_next():
                    # Create a new form for a following step, if the following step is present
                    form_class = self.get_form_class_for_step(step)
                    form = form_class(page=self, user=request.user)
                else:
                    # If there is no more steps, create form for all fields
                    form = self.get_form(
                        request.session[session_key_data],
                        page=self, user=request.user
                    )

                    if form.is_valid():
                        # Perform validation again for whole form.
                        # After successful validation, save data into DB,
                        # and remove from the session.
                        self.process_form_submission(form)
                        del request.session[session_key_data]

                        # Render the landing page
                        return render(
                            request,
                            self.landing_page_template,
                            self.get_context(request)
                        )
            else:
                # If data for step is invalid
                # we will need to display form again with errors,
                # so restore previous state.
                form = prev_form
                step = prev_step
        else:
            # Create empty form for non-POST requests
            form_class = self.get_form_class_for_step(step)
            form = form_class(page=self, user=request.user)

        context = self.get_context(request)
        context['form'] = form
        context['fields_step'] = step
        return render(
            request,
            self.template,
            context
        )


class SurveyWithPaginationFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyWithPaginationPage, related_name='survey_form_fields')

```

Now you need to create a template like this:

```django
{% load wagtailcore_tags %}
<html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>
        <h1>{{ page.title }}</h1>

        <div>{{ self.intro|richtext }}</div>
        <form action="{% pageurl self %}?p={{ fields_step.number|add:"1" }}" method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit">
        </form>
    </body>
</html>
```

Note that the example shown before allows the user to return to a previous step,
or to open a second step without submitting the first step.
Depending on your requirements, you may need to add extra checks.

#### Show results

For some polls or surveys, you may need show results.
The following example demonstrates how to do this.

At first, you need to collect results as shown below:

```python
from modelcluster.fields import ParentalKey

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField

from wagtailsurveys import models as surveys_models

class SurveyWithResultsPage(surveys_models.AbstractSurvey):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = surveys_models.AbstractSurvey.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('survey_form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(SurveyWithResultsPage, self).get_context(request, *args, **kwargs)

        # If you need to show results only on landing page,
        # you may need check request.method

        results = dict()
        # Get information about form fields
        data_fields = [
            (field.clean_name, field.label)
            for field in self.get_form_fields()
        ]

        # Get all submissions for current page
        submissions = self.get_submission_class().objects.filter(page=self)
        for submission in submissions:
            data = submission.get_data()

            # Count results for each question
            for name, label in data_fields:
                answer = data.get(name)
                if answer is None:
                    # Something wrong with data.
                    # Probably you have changed questions
                    # and now we are receiving answers for old questions.
                    # Just skip them.
                    continue

                if type(answer) is list:
                    # Answer is a list if the field type is 'Checkboxes'
                    answer = u', '.join(answer)

                question_stats = results.get(label, {})
                question_stats[answer] = question_stats.get(answer, 0) + 1
                results[label] = question_stats

        context.update({
            'results': results,
        })
        return context


class SurveyWithResultsFormField(surveys_models.AbstractFormField):
    page = ParentalKey(SurveyWithResultsPage, related_name='survey_form_fields')

```

Now you need create a template like this:

```django
{% load wagtailcore_tags %}
<html>
    <head>
        <title>{{ page.title }}</title>
    </head>
    <body>
        <h1>{{ page.title }}</h1>

        <h2>Results</h2>
        {% for question, answers in results.items %}
            <h3>{{ question }}</h3>
            {% for answer, count in answers.items %}
                <div>{{ answer }}: {{ count }}</div>
            {% endfor %}
        {% endfor %}

        <div>{{ self.intro|richtext }}</div>
        <form action="{% pageurl self %}" method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit">
        </form>
    </body>
</html>
```

You can also show the results on the landing page.

## How to run tests

To run tests you need to clone this repository:

    git clone https://github.com/torchbox/wagtailsurveys.git
    cd wagtailsurveys

With your preferred virtualenv activated, install the testing dependencies:

    pip install -e .[testing] -U

Now you can run tests as shown below:

    python runtests.py
