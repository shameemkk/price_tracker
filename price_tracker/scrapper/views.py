from django.shortcuts import redirect, render
from django.contrib import messages
from .tasks import get_data_from_url
from .models import TaskStatus
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):
    """
    Render the index page.
    """
    return render(request, 'index.html')

@login_required(login_url='/auth/login/')       
def fetch_html(request):
    """
    Fetch and return product price from a given URL.
    """
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            messages.error(request, 'URL fields are required.')
            return render(request, 'index.html')
        task_status = TaskStatus.objects.create(user=request.user, url=url, status='pending')
        get_data_from_url.delay(url,task_status.id)
        return redirect('task_status')
    return render(request, 'index.html')

@login_required(login_url='/auth/login/')
def task_status(request):
    """
    Fetch and return the status of a tasks.
    """
    tasks= TaskStatus.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'task_status.html', {'tasks': tasks})