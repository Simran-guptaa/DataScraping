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
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        product = soup.find('div', {'data-component-type': 's-search-result'})
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
    except Exception as e:
        return {'Website': 'Amazon', 'Error': str(e)}

def scrape_flipkart(search_term):
    search_url = f"https://www.flipkart.com/search?q={search_term.replace(' ', '%20')}"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(search_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div._1YokD2'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        products = soup.find_all('div', class_='_1AtVbE')
        if not products:
            return {'Website': 'Flipkart', 'Error': 'No products found'}

        product = products[0]  # Just picking the first product (you can change this logic)

        title = product.find('div', class_='_4rR01T').text.strip() if product.find('div', class_='_4rR01T') else "N/A"
        price = product.find('div', class_='_30jeq3').text.strip() if product.find('div', class_='_30jeq3') else "N/A"
        
        # Check for offer price or discount price
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

    finally:
        driver.quit() 

def scrape_croma(search_term):
    search_url = f"https://www.flipkart.com/search?q={search_term.replace(' ', '%20')}"
 
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU usage
    options.add_argument('--no-sandbox')  # Required in Render environment
    options.add_argument('--disable-dev-shm-usage')  # Prevent shared memory issues

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(search_url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div._1YokD2'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all('div', class_='_1AtVbE')

        if not products:
            return {'Website': 'Flipkart', 'Error': 'No products found'}

        # Extract the first product
        product = products[0]
        title = product.find('div', class_='_4rR01T').text.strip() if product.find('div', class_='_4rR01T') else "N/A"
        price = product.find('div', class_='_30jeq3').text.strip() if product.find('div', class_='_30jeq3') else "N/A"
        offer_price = product.find('div', class_='_3I9_wc')
        offer_price = offer_price.text.strip() if offer_price else "N/A"

        return {
            'Website': 'Flipkart',
            'Title': title,
            'Price': price,
            'Offer Price': offer_price,
        }
    except Exception as e:
        return {'Website': 'Flipkart', 'Error': str(e)}
    finally:
        if 'driver' in locals():
            driver.quit()


# Function to scrape data from Myntra 
def scrape_myntra(search_term):
    url = f"https://www.myntra.com/s?k={search_term.replace(' ', '+')}"
    options = Options()
    options.headless = True  
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'pdp-title'))
        )
        title = driver.find_element(By.CLASS_NAME, 'pdp-title').text.strip()

        try:
            price = driver.find_element(By.CLASS_NAME, 'PriceInfo-mrp').text.strip()
        except:
            price = "Price not found"

        try:
            offer_price = driver.find_element(By.CLASS_NAME, 'pdp-price').text.strip()
        except:
            offer_price = "Offer Price not found"

        try:
            rating = driver.find_element(By.CLASS_NAME, 'index-overallRating').text.strip()
        except:
            rating = "Rating not found"

        try:
            review = driver.find_element(By.CLASS_NAME, 'detailed-reviews-headline').text.strip()
        except:
            review = "Review not found"

        return {'Website': 'Myntra', 'Title': title, 'Price': price, 'Offer Price': offer_price, 'Rating': rating, 'Review': review, 'Product Link': url}

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {'Website': 'Myntra', 'Title': 'N/A','Price': 'N/A','Offer Price': 'N/A','Rating': 'N/A','Review': 'N/A','Product Link': url}
    finally:
        driver.quit()

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    amazon_data = scrape_amazon(search_term)
    flipkart_data = scrape_flipkart(search_term)
    croma_data = scrape_croma(search_term)
    myntra_data = scrape_myntra(search_term) 
    return jsonify([amazon_data, flipkart_data, croma_data, myntra_data])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')

 