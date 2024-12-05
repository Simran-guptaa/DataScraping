from flask import Flask, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus

app = Flask(__name__)

def scrape_amazon(search_term):
    base_url = f"https://www.amazon.in/s?k={search_term.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('div', {'data-component-type': 's-search-result'})
        if not product:
            return {'Website': 'Amazon', 'Error': 'No products found'}

        title = product.h2.text.strip()
        link = "https://www.amazon.in" + product.h2.a['href']
        price = product.find('span', class_='a-price a-text-price')
        price = price.text.strip() if price else 'N/A'

        offer_price = product.find('span', class_='a-price-whole')
        offer_price = offer_price.text.strip() if offer_price else 'N/A'

        rating = product.find('span', class_='a-icon-alt')
        rating = rating.text.strip() if rating else 'N/A'
        review_count = product.find('span', class_='a-size-base')
        review_count = review_count.text.strip() if review_count else 'N/A'

        return {
            'Website': 'Amazon',
            'Title': title,
            'Price': price,
            'Offer Price': offer_price,
            'Rating': rating,
            'Reviews Count': review_count,
            'Product Link': link
        }
    except requests.exceptions.RequestException as e:
        return {'Website': 'Amazon', 'Error': f"Request failed: {str(e)}"}
    except Exception as e:
        return {'Website': 'Amazon', 'Error': str(e)}

def scrape_flipkart(search_term):
    base_url = f"https://www.flipkart.com/search?q={quote_plus(search_term)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('div', {'class': '_1AtVbE'})
        if not product:
            return {'Website': 'Flipkart', 'Error': 'No products found'}

        title = product.find('div', class_='_4rR01T').text.strip() if product.find('div', class_='_4rR01T') else "N/A"
        price = product.find('div', class_='_30jeq3').text.strip() if product.find('div', class_='_30jeq3') else "N/A"
        offer_price = product.find('div', class_='_3I9_wc')
        offer_price = offer_price.text.strip() if offer_price else "N/A"

        rating = product.find('div', class_='_3LWZlK').text.strip() if product.find('div', class_='_3LWZlK') else "No rating"
        review_count = product.find('span', class_='_2_R_DZ').text.strip() if product.find('span', class_='_2_R_DZ') else "No reviews"
        product_link = "https://www.flipkart.com" + product.find('a', class_='_1fQZEK')['href'] if product.find('a', class_='_1fQZEK') else "N/A"

        return {
            'Website': 'Flipkart',
            'Title': title,
            'Price': price,
            'Offer Price': offer_price,
            'Rating': rating,
            'Reviews Count': review_count,
            'Product Link': product_link
        }

    except Exception as e:
        return {'Website': 'Flipkart', 'Error': str(e)}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/search', methods=['POST'])
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    website = request.form.get('website', 'both')  # Accept a 'website' parameter to specify Amazon, Flipkart, or both.

    results = []

    if website == 'amazon' or website == 'both':
        try:
            amazon_data = scrape_amazon(search_term)
            results.append(amazon_data)
        except Exception as e:
            results.append({"error": f"Error scraping Amazon: {str(e)}"})

    if website == 'flipkart' or website == 'both':
        try:
            flipkart_data = scrape_flipkart(search_term)
            results.append(flipkart_data)
        except Exception as e:
            results.append({"error": f"Error scraping Flipkart: {str(e)}"})

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

 