import os
from wagtail import VERSION as WAGTAIL_VERSION


WAGTAILMEDIA_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(WAGTAILMEDIA_ROOT, 'test-static')
MEDIA_ROOT = os.path.join(WAGTAILMEDIA_ROOT, 'test-media')
MEDIA_URL = '/media/'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', 'wagtailsurveys'),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASS', None),
        'HOST': os.environ.get('DATABASE_HOST', None),

        'TEST': {
            'NAME': os.environ.get('DATABASE_NAME', None),
        }
    }
}


SECRET_KEY = 'not needed'

ROOT_URLCONF = 'wagtailsurveys.tests.urls'

STATIC_URL = '/static/'
STATIC_ROOT = STATIC_ROOT

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'wagtail.contrib.settings.context_processors.settings',
            ],
            'debug': True,
        },
    }
]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if WAGTAIL_VERSION < (2, 0):
    MIDDLEWARE_CLASSES = [
        'wagtail.wagtailcore.middleware.SiteMiddleware',
        'wagtail.wagtailredirects.middleware.RedirectMiddleware',
    ] + MIDDLEWARE_CLASSES
else:
    MIDDLEWARE_CLASSES = [
        'wagtail.core.middleware.SiteMiddleware',
        'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    ] + MIDDLEWARE_CLASSES


INSTALLED_APPS = [
    'wagtailsurveys.tests.testapp',
    'wagtailsurveys',

    'taggit',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]


if WAGTAIL_VERSION < (2, 0):
    INSTALLED_APPS = [
        'wagtail.wagtailredirects',
        'wagtail.wagtailimages',
        'wagtail.wagtailusers',
        'wagtail.wagtaildocs',
        'wagtail.wagtailadmin',
        'wagtail.wagtailcore',
    ] + INSTALLED_APPS
else:
    INSTALLED_APPS = [
        'wagtail.contrib.redirects',
        'wagtail.images',
        'wagtail.users',
        'wagtail.documents',
        'wagtail.admin',
        'wagtail.core',
    ] + INSTALLED_APPS


# Using DatabaseCache to make sure THAT the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # don't use the intentionally slow default password hasher
)


if WAGTAIL_VERSION < (2, 0):
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.wagtailsearch.backends.db',
        }
    }
else:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': 'wagtail.search.backends.db',
        }
    }


WAGTAIL_SITE_NAME = "Test Site"
