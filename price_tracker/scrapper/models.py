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
