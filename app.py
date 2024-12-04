from flask import Flask, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Scrape Amazon
def scrape_amazon(search_term):
    logging.info(f"Scraping Amazon for search term: {search_term}")
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
        logging.error(f"Request error: {e}")
        return {'Website': 'Amazon', 'Error': f"Request failed: {str(e)}"}
    except Exception as e:
        logging.error(f"Scraping error: {e}")
        return {'Website': 'Amazon', 'Error': str(e)}

# Serve index.html
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Search endpoint
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    try:
        amazon_data = scrape_amazon(search_term)
        return jsonify([amazon_data])
    except Exception as e:
        logging.error(f"Search endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
