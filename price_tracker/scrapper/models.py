from django.db import models


class PriceSelector(models.Model):
    """Model for storing price selector configurations for different domains"""
    domain = models.CharField(max_length=100, help_text="Website domain name")
    tag = models.CharField(max_length=100, null=True, choices=[('span', 'span'), ('div', 'div')], help_text="HTML tag (span or div) containing the price")
    css_selector = models.CharField(max_length=100, null=True, choices=[('id', 'id'), ('class', 'class')], help_text="CSS selector type (id or class)")
    value= models.CharField(max_length=100,null=True)

    class Meta:
        verbose_name = "Price Selector"

    def __str__(self):
        return f"{self.domain} - {self.css_selector}"

class TaskStatus(models.Model):
    """Model for storing the status of tasks"""
    url= models.URLField(max_length=200, help_text="URL of the page to be scraped")
    status = models.CharField(max_length=20, help_text="Current status of the task (e.g., pending, completed, failed)")
    result = models.TextField(null=True, blank=True, help_text="Result of the task execution")
    error_message = models.TextField(null=True, blank=True, help_text="Error message if error occurs during task execution")
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, help_text="User who initiated the task")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the task was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the task was last updated")

    class Meta:
        verbose_name = "Task Status"

    def __str__(self):
        return f"Task {self.task_id} - {self.status}"