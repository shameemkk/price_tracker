from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import tldextract
import json
import requests


def fetch_clean_html(url: str):
  
    """Fetches and cleans HTML content from a given URL using Selenium WebDriver.
    
    This function uses Selenium with Chrome WebDriver to load a webpage, wait for the content
    to load, and then clean the HTML by removing unwanted elements like scripts, styles, etc.
    
    Args:
        url (str): The URL of the webpage to fetch and clean
        
    Returns:
        str: The cleaned HTML content as a string, with unwanted elements removed
             Returns "Error" if any exception occurs during the process
    """
 
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Remove unwanted tags
        for tag in soup(["script", "style", "link", "noscript", "input", "iframe", "a", "img", "option", "table", "ul", "li", "title", "path", "svg"]):
            tag.decompose()
        # Return clean HTML
        clean_html = soup.prettify()
        clean_html = str(clean_html).replace('\n', '').replace('\r', '').replace('\t', '')
        clean_html = str(clean_html).replace('  ', ' ').replace('> <', '><')
        clean_html = clean_html.strip()
        return clean_html

    except Exception as e:
        print(f"Error: {e}")
        return "Error"
    finally:
        driver.quit()


def extract_domain_from_url(url :str) -> str:
    """Extracts the domain name from a given URL.
    
    This function uses tldextract to parse a URL and extract just the domain name
    portion, excluding subdomains and TLD.
    
    Args:
        url (str): The URL to extract the domain from
        
    Returns:
        str: The domain name portion of the URL
    """
    extracted = tldextract.extract(url)  
    site_name = extracted.domain 
    return site_name

def fetch_ai_analysis(data):
    """Fetches AI analysis for the given HTML data using OpenRouter API.
    
    This function sends a POST request to the OpenRouter API with the provided HTML data
    and retrieves the AI-generated analysis in JSON format.
    
    Args:
        data (str): The HTML content to be analyzed
        
    Returns:
        dict: The AI-generated analysis in JSON format, or None if an error occurs
    """
    prompt = f"""
    Extract the main product price from the given HTML {data}. Multiple prices may exist, but fetch only the main product price — usually a parent <span> or <div> element.
    Return the result in this exact Python dictionary format, under the key data:
    {{
    "data": {{
        "product_name": "...",
        "product_price_css_selector": {{
        "tag": "div or span",
        "selector": "id or class",
        "value": "value of the id or class"
        }},
        "price": "..."
    }}
    }}
    Only return the dictionary. Do not include any explanations, comments, or extra text.
    """
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer <API_KEY>",
        "Content-Type": "application/json",

    },
    data=json.dumps({
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
        {
            "role": "user",
            "content": prompt
        }
        ],

    })
    )
    return response