from django.conf import settings

def app_config(request):
    return {
        'APP_NAME': settings.APP_NAME,
        'DEV_CONTACT': settings.DEV_CONTACT,
    }
