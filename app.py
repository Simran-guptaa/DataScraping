from flask import Flask, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import requests
import logging
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Scrape Amazon function
def scrape_amazon(search_term):
    """
    Scrapes Amazon for product data.
    """
    logging.info(f"Scraping Amazon for search term: {search_term}")
    base_url = f"https://www.amazon.in/s?k={search_term.replace(' ', '+')}"
    
    # Set up headers to mimic a browser
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    # Create a session with retries for handling 503 errors
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[503])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        # Add random delay to reduce chances of being blocked
        time.sleep(random.uniform(2, 5))
        response = session.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first product
        product = soup.find('div', {'data-component-type': 's-search-result'})
        if not product:
            return {'Website': 'Amazon', 'Error': 'No products found'}

        # Extract product details
        title = product.h2.text.strip()
        link = "https://www.amazon.in" + product.h2.a['href']
        price = product.find('span', class_='a-price')
        price = price.find('span', class_='a-offscreen').text.strip() if price else "N/A"
        rating = product.find('span', class_='a-icon-alt')
        rating = rating.text.strip() if rating else "N/A"
        reviews_count = product.find('span', class_='a-size-base')
        reviews_count = reviews_count.text.strip() if reviews_count else "N/A"

        return {
            'Website': 'Amazon',
            'Title': title,
            'Price': price,
            'Rating': rating,
            'Reviews Count': reviews_count,
            'Product Link': link
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return {'Website': 'Amazon', 'Error': f"Request failed: {e}"}
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        return {'Website': 'Amazon', 'Error': str(e)}

# Serve index.html
@app.route('/')
def home():
    """
    Serves the home page.
    """
    return send_from_directory('.', 'index.html')

# Search endpoint
@app.route('/search', methods=['POST'])
def search():
    """
    Handles the search request.
    """
    search_term = request.form.get('search_term')
    try:
        amazon_data = scrape_amazon(search_term)
        return jsonify([amazon_data])
    except Exception as e:
        logging.error(f"Search endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
