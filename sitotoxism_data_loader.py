from dotenv import load_dotenv
import os
import requests

load_dotenv()

def fetch_sitotoxism_data(dataset_code : str):

    sitotoxism_api_key = os.getenv('SITOTOXISM_API_KEY')

    initial_url = f"http://openapi.foodsafetykorea.go.kr/api/{sitotoxism_api_key}/{dataset_code}/json/1/1"
    
    initial_response = requests.get(initial_url)

    total_count = int(initial_response.json()[dataset_code].get("total_count", 0))

    rows = []

    batch_size = 1000

    for start in range(1, total_count + 1, batch_size):

        end = min(start + batch_size - 1, total_count)

        url = f"http://openapi.foodsafetykorea.go.kr/api/{sitotoxism_api_key}/{dataset_code}/json/{start}/{end}"
        
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            rows.extend(data[dataset_code].get("row", []))
            
        else:
            break
    
    return rows