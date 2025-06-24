from celery import shared_task
from bs4 import BeautifulSoup
import json
from .models import PriceSelector, TaskStatus
from .utils import fetch_clean_html, extract_domain_from_url, fetch_ai_analysis
import logging


@shared_task
def get_data_from_url(url, task_id=None):
    """
    Celery task to fetch price data from a URL, update TaskStatus, and handle errors robustly.
    """
    try:
        domain = extract_domain_from_url(url)
        price_selector, created = PriceSelector.objects.get_or_create(domain=domain)
        clean_html = fetch_clean_html(url)
        if clean_html == "Error":
            if task_id:
                TaskStatus.objects.filter(id=task_id).update(status='failed', error_message='Failed to fetch HTML.')
            return None
        if created or price_selector.tag is None:
            response = fetch_ai_analysis(clean_html)
            if response is not None:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    try:
                        formated_data = json.loads(content)
                        price_selector.tag = formated_data['data']['product_price_css_selector']['tag']
                        price_selector.css_selector = formated_data['data']['product_price_css_selector']['selector']
                        price_selector.value = formated_data['data']['product_price_css_selector']['value']
                        price_selector.save()
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decoding error: {e}")
                        if task_id:
                            TaskStatus.objects.filter(id=task_id).update(status='failed', error_message=f'AI JSON decode error: {e}')
                        return None
                else:
                    if task_id:
                        TaskStatus.objects.filter(id=task_id).update(status='failed', error_message='AI analysis did not return choices.')
                    return None
            else:
                if task_id:
                    TaskStatus.objects.filter(id=task_id).update(status='failed', error_message='AI analysis response is None.')
                return None
        soup = BeautifulSoup(clean_html, "html.parser")
        price_span = None
        if price_selector.css_selector == 'class':
            price_span = soup.find(str(price_selector.tag), class_=str(price_selector.value))
        elif price_selector.css_selector == 'id':
            price_span = soup.find(str(price_selector.tag), id=str(price_selector.value))
        price = None
        if price_span:
            price = price_span.text.strip().split()[0].replace(',', '')
            if task_id:
                TaskStatus.objects.filter(id=task_id).update(status='completed', result=price)
        else:
            if task_id:
                TaskStatus.objects.filter(id=task_id).update(status='failed', error_message='Price element not found.')
        return price
    except Exception as e:
        logging.exception("Error in get_data_from_url")
        if task_id:
            TaskStatus.objects.filter(id=task_id).update(status='failed', error_message=str(e))
        return None

