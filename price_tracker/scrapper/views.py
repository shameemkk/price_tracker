from django.shortcuts import render
from .utils import fetch_clean_html, extract_domain_from_url, fetch_ai_analysis
from .models import PriceSelector
from django.contrib import messages
from bs4 import BeautifulSoup
import json

# Create your views here.

def index(request):
    """
    Render the index page.
    """
    return render(request, 'index.html')

def fetch_html(request):
    """
    Fetch and return clean HTML from a given URL.
    """
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            messages.error(request, 'Both fields are required.')
            return render(request, 'index.html')
        domain = extract_domain_from_url(url) 
        price_selector, created = PriceSelector.objects.get_or_create(domain=domain)
        clean_html = fetch_clean_html(url)
        if clean_html == "Error":
            return render(request, 'fetch_html.html', {'error': 'Failed to fetch HTML.'})
        elif created or price_selector.tag is None:
            print('ai analyse need to be done')
            response = fetch_ai_analysis(clean_html)
            if response is not None:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    print(content)
                    try:
                        formated_data = json.loads(content)
                        price_selector.tag = formated_data['data']['product_price_css_selector']['tag']
                        price_selector.css_selector = formated_data['data']['product_price_css_selector']['selector']
                        price_selector.value = formated_data['data']['product_price_css_selector']['value']
                        price_selector.save()
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding error: {e}")
            else:
                print("AI analysis response is None")
        else:
            soup = BeautifulSoup(clean_html, "html.parser")
            price_span=None
            print(price_selector.tag, price_selector.css_selector, price_selector.value)
            if price_selector.css_selector == 'class':
                price_span = soup.find(str(price_selector.tag), class_=str(price_selector.value))
            elif price_selector.css_selector == 'id':
                price_span = soup.find(str(price_selector.tag), id=str(price_selector.value))
            if price_span:
                print(price_span.text.strip().split()[0].replace(',', ''))
                price= price_span.text.strip().split()[0].replace(',', '')
        return render(request, 'fetch_html.html', {'price': price}) # type: ignore

    return render(request, 'index.html')


