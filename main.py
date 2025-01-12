import requests
import pandas as pd
import time
from datetime import datetime
import os
import logging

# Setup Logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("error.log")
file_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Fetch Comment
def fetch_comments(shopid, userid, rating_type, offset):
    url = f'https://shopee.co.id/api/v4/seller_operation/get_shop_ratings_new'
    params = {
        'limit': 100,
        'offset': offset,
        'shopid': shopid,
        'type': rating_type,
        'userid': userid
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Request failed with exception: {e}")
        return None

def process_comments(data):
    comments = []
    for item in data:
        try:
            comments.append({
                'Shop ID': item.get('shopid'),
                'Buyer ID': item.get('userid'),
                'Item ID': item.get('itemid'),
                'Time': datetime.fromtimestamp(item.get('submit_time', 0)),
                'Rating': item.get('rating_star'),
                'Comment': item.get('comment')
            })
        except Exception as e:
            logger.error(f"Error processing comment: {e}")
    return comments

def save_to_csv(data, output_file):
    if data:
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Data saved successfully to {output_file}")
    else:
        logger.error("No data to save.")

def scrape_shopee_comments(shopid, userid, output_file):
    comment_list = []

    for rating_type in range(1, 6):
        offset = 0
        while True:
            logger.info(f"Fetching comments for rating {rating_type}, offset {offset}...")
            response_data = fetch_comments(shopid, userid, rating_type, offset)

            # Handle invalid response data gracefully
            if not isinstance(response_data, dict):
                logger.error("Invalid response received. Please check the shop ID or user ID.")
                break

            # Check if the response contains valid data
            if not response_data or 'data' not in response_data or not response_data['data'].get('items'):
                logger.info(f"No more comments to fetch for rating type {rating_type}.")
                break

            try:
                comments = process_comments(response_data['data']['items'])
                comment_list.extend(comments)
            except Exception as e:
                logger.error(f"Error while processing comments: {e}")

            offset += 100
            time.sleep(5)

    try:
        save_to_csv(comment_list, output_file)
    except Exception as e:
        logger.error(f"Failed to save data: {e}")

def main():
    # Update the test cases
    shop_user_pairs = [
        {'shop_id': 195455930, 'user_id': 17567755, 'output_file': "Shopee_scrapper/comments_somethinc_195455930.csv"},
        # Uncomment or add more cases as needed
        # {'shop_id': 380285841, 'user_id': 380285841, 'output_file': "Shopee_scrapper/comments_skintific.csv"},
        # {'shop_id': 255365082, 'user_id': 255366005, 'output_file': "Shopee_scrapper/comments_scarlett.csv"},
        # {'shop_id': 62583853, 'user_id': 62585295, 'output_file': "Shopee_scrapper/comments_ganier.csv"},
        # {'shop_id': 17566419, 'user_id': 17567755, 'output_file': "Shopee_scrapper/comments_msglow.csv"}
    ]

    for pair in shop_user_pairs:
        shop_id = pair['shop_id']
        user_id = pair['user_id']
        output_file = pair['output_file']

        logger.info(f"Starting scrape for Shop ID: {shop_id}, User ID: {user_id}")
        try:
            scrape_shopee_comments(shop_id, user_id, output_file)
        except Exception as e:
            logger.error(f"Error while scraping comments for Shop ID: {shop_id}, User ID: {user_id}. Exception: {e}")

        time.sleep(10)

if __name__ == "__main__":
    main()
