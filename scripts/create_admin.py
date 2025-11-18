import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'pio_o_connell@gmail.com', 'admin')
    print('CREATED')
else:
    print('ALREADY_EXISTS')

