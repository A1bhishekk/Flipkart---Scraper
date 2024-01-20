
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import os
import re

def scrape_flipkart_products(base_url, num_pages=2):
    # Initialize lists to store data
    name = []
    price = []
    link = []
    image_link = []

    # URL pattern for different pages
    url_pattern = base_url + "&page={}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }

    os.makedirs("images", exist_ok=True)
    
    # Use tqdm to create a progress bar
    for page in tqdm(range(1, num_pages + 1), desc="Extraction Completed"):
        product_url = url_pattern.format(page)
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
        

    # Save images to the 'images' folder
    for i, img_url in enumerate(image_link):
        if img_url:
            img_response = requests.get(img_url)

            # Create a safe filename by removing invalid characters
            img_name = re.sub(r"[^\w\d.]+", "_", name[i])[:100]  # Limit filename length to 100 characters
            img_name = f"images/{img_name}_img{i + 1}.jpg"

            with open(img_name, "wb") as img_file:
                img_file.write(img_response.content)
    # Save to CSV file
    data = pd.DataFrame({
        "Name": name,
        "Price": price,
        "Image": image_link,
        "Link": link
    })

    data.to_csv("Laptop_products_all_pages.csv", index=False)
    print("Done")

# Example usage:
base_url = "https://www.flipkart.com/search?q=smartphone+under+30000&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
base_url = "https://www.flipkart.com/search?q=laptop+under+70000&sid=6bo%2Cb5g&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_17_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_17_na_na_na&as-pos=1&as-type=RECENT&suggestionId=laptop+under+70000%7CLaptops&requestId=9081c30c-f926-48f6-bd41-6b36f4593652&as-searchtext=laptop%20under%207000"

num_pages = 2
scrape_flipkart_products(base_url, num_pages)