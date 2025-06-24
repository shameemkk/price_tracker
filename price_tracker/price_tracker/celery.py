import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'price_tracker.settings')

app = Celery('price_tracker')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
