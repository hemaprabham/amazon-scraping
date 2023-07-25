import csv
import requests
from bs4 import BeautifulSoup
import time

# Function to scrape product details from a product listing page
def scrape_product_listing(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    results = []
    for product in products:
        product_url = "https://www.amazon.in" + product.find("a", class_="a-link-normal")["href"]
        product_name = product.find("span", class_="a-size-medium").text.strip()
        product_price = product.find("span", class_="a-offscreen").text.strip()
        product_rating = product.find("span", class_="a-icon-alt").text.strip().split()[0]
        num_reviews = product.find("span", class_="a-size-base").text.strip()

        results.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": product_rating,
            "Number of Reviews": num_reviews
        })

    return results

# Function to scrape product details from a product detail page
# Function to scrape product details from a product detail page
def scrape_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    product_description = soup.find("div", {"id": "productDescription"}).text.strip() if soup.find("div", {"id": "productDescription"}) else ""
    manufacturer = soup.find("a", {"id": "bylineInfo"}).text.strip() if soup.find("a", {"id": "bylineInfo"}) else ""

    # Handle ASIN extraction with proper error handling
    try:
        asin = soup.find("th", string="ASIN").find_next("td").text.strip()
    except AttributeError:
        asin = ""

    return {
        "ASIN": asin,
        "Product Description": product_description,
        "Manufacturer": manufacturer
    }

# Main function to initiate scraping
def main():
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"
    num_pages = 20

    # Scrape product listing pages
    all_products = []
    for page_num in range(1, num_pages + 1):
        page_url = base_url.format(page_num)
        print("Scraping page:", page_num)
        all_products.extend(scrape_product_listing(page_url))
        time.sleep(2)  # Adding a small delay to avoid overwhelming the server

    # Scrape product detail pages
    num_products_to_scrape = 200
    num_products_scraped = 0

    for product in all_products:
        if num_products_scraped >= num_products_to_scrape:
            break

        print("Scraping product:", product["Product Name"])
        product_details = scrape_product_details(product["Product URL"])
        product.update(product_details)

        num_products_scraped += 1
        time.sleep(2)  # Adding a small delay to avoid overwhelming the server

    # Export data to CSV
    csv_file = "amazon_products.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", "ASIN", "Product Description", "Manufacturer"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_products)

    print("Data has been scraped and exported to", csv_file)

if __name__ == "__main__":
    main()
