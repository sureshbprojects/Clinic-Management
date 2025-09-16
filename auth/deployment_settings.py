import os
import dj_database_url
from .settings import *
from .settings import BASE_DIR

ALLOWED_HOSTS=[os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

# Get the hostname from the environment
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

# Trust both the www and non-www versions
if render_hostname:
    CSRF_TRUSTED_ORIGINS = [
        f'https://{render_hostname}',
        f'https://www.{render_hostname}',
    ]
else:
    # Fallback for local development if the env var isn't set
    CSRF_TRUSTED_ORIGINS = [] 

DEBUG=False
SECRET_KEY=os.environ.get('SECRET_KEY')


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS_ALLOWED_ORIGINS = [
#  'http://localhost:5173',
# ]

STORAGES={
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    }  
}

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
    
}