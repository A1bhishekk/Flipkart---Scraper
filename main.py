import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from termcolor import colored

def scrape_page(page_num, base_url):
    # Initialize lists to store data for a single page
    name = []
    price = []
    link = []
    image_link = []

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/94.0.4606.81 Safari/537.36"
    }

    product_url = base_url + "&page={}".format(page_num)
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract data from the current page
    for product in soup.find_all('div', class_='_2kHMtA'):
        product_name = product.find('div', class_='_4rR01T')
        product_price = product.find('div', class_='_30jeq3 _1_WHN1')
        product_link = product.find('a', class_='_1fQZEK')
        product_image = product.find('img', class_='_396cs4')

        # Check if elements are found before accessing their text attribute
        if product_name:
            name.append(product_name.text)
        else:
            name.append(None)

        if product_price:
            price.append(product_price.text)
        else:
            price.append(None)

        if product_link and 'href' in product_link.attrs:
            link.append("https://www.flipkart.com" + product_link['href'])
        else:
            link.append(None)

        if product_image and 'src' in product_image.attrs:
            image_link.append(product_image['src'])
        else:
            image_link.append(None)

    return name, price, link, image_link

def scrape_flipkart_products(base_url, num_pages=2, num_threads=5):
    # Use tqdm to create a progress bar
    with tqdm(total=num_pages,desc=colored("Extraction Complete ☠️☠️", "red") ,colour="MAGENTA") as pbar:
        # Initialize lists to store data
        all_names = []
        all_prices = []
        all_links = []
        all_image_links = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit tasks for each page to the thread pool
            futures = [executor.submit(scrape_page, page, base_url) for page in range(1, num_pages + 1)]

            # Process completed tasks
            for future in futures:
                name, price, link, image_link = future.result()
                all_names.extend(name)
                all_prices.extend(price)
                all_links.extend(link)
                all_image_links.extend(image_link)
                pbar.update(1)

    # Save to CSV file
    data = pd.DataFrame({
        "Name": all_names,
        "Price": all_prices,
        "Image": all_image_links,
        "Link": all_links
    })

    data.to_csv("top_smartphones.csv", index=False)
    print(colored("Extraction Completed Successfull 🚀🚀", "green"))

# Example usage:
base_url = "https://www.flipkart.com/search?q=smartphone+under+30000&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
num_pages = 45
num_threads = 12
scrape_flipkart_products(base_url, num_pages, num_threads)
