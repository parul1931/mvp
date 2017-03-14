import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mvp',
        'USER': 'root',
        'PASSWORD': 'pankaj#',
        'HOST': 'localhost',
        'PORT': '',
    }
}

DEBUG = True