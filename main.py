import requests
import pandas as pd
import time
from datetime import datetime
import os

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
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
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
            print(f"Error processing comment: {e}")
    return comments

def save_to_csv(data, output_file):
    if data:
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved successfully to {output_file}")
    else:
        print("No data to save.")

def scrape_shopee_comments(shopid, userid, output_file):
    comment_list = []

    for rating_type in range(1, 6):
        offset = 0
        while True:
            print(f"Fetching comments for rating {rating_type}, offset {offset}...")
            response_data = fetch_comments(shopid, userid, rating_type, offset)

            if not response_data or 'data' not in response_data or not response_data['data']['items']:
                print("No more comments to fetch.")
                break

            comments = process_comments(response_data['data']['items'])
            comment_list.extend(comments)

            offset += 100
            time.sleep(5)  

    save_to_csv(comment_list, output_file)

def main():
    shop_user_pairs = [
        {'shop_id': 195455930, 'user_id': 195458863, 'output_file': "../Shopee_scrapper/comments_somethinc.csv"},
        {'shop_id': 380285841, 'user_id': 380285841, 'output_file': "../Shopee_scrapper/comments_skintific.csv"},
        {'shop_id': 255365082, 'user_id': 255366005, 'output_file': "../Shopee_scrapper/comments_scarlett.csv"},
        {'shop_id': 62583853, 'user_id': 62585295, 'output_file': "../Shopee_scrapper/comments_ganier.csv"},
        {'shop_id': 17566419, 'user_id': 17567755, 'output_file': "../Shopee_scrapper/comments_msglow.csv"}
    ]

    for pair in shop_user_pairs:
        shop_id = pair['shop_id']
        user_id = pair['user_id']
        output_file = pair['output_file']

        print(f"Starting scrape for Shop ID: {shop_id}, User ID: {user_id}")
        scrape_shopee_comments(shop_id, user_id, output_file)

        time.sleep(10)

if __name__ == "__main__":
    main()
