from datetime import datetime, timedelta, timezone
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import requests

def get_base_datetime():

    kst = timezone(timedelta(hours = 9))
    now = datetime.now(timezone.utc).astimezone(kst)

    available_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    current_hour = now.hour

    base_hour = max([h for h in available_hours if h <= current_hour], default = 23)

    if current_hour < 2:
        now -= timedelta(days = 1)

    base_date = now.strftime('%Y%m%d')
    base_time = f'{base_hour:02}00'

    return base_date, base_time

def get_grid_from_address(address):

    vectorstore = Chroma(
        persist_directory = "./grid_db",
        embedding_function = OpenAIEmbeddings(model = "text-embedding-3-large"),
        collection_name = "g_db"
    )

    result = vectorstore.similarity_search(query = address, k = 1)

    if not result:
        raise ValueError("해당 주소에 대한 격자 정보를 찾을 수 없습니다.")
    
    result_doc = result[0]

    return result_doc.metadata['x'], result_doc.metadata['y']

def fetch_weather_data(address):

    load_dotenv()

    weather_api_key = os.getenv('WEATHER_API_KEY')

    base_date, base_time = get_base_datetime()

    nx, ny = get_grid_from_address(address)

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

    params = {
        'serviceKey' : weather_api_key,
        'pageNo' : '1',
        'numOfRows' : '1000',
        'dataType' : 'JSON',
        'base_date' : base_date,
        'base_time' : base_time,
        'nx' : nx,
        'ny' : ny
    }

    response = requests.get(url, params = params)

    return response.json()

def extract_weather_fields(data):

    items = data['response']['body']['items']['item']

    summaries = []

    for item in items:

        summary = {
            "category" : item["category"],
            "fcstDate" : item["fcstDate"],
            "fcstTime" : item["fcstTime"],
            "fcstValue" : item["fcstValue"]
        }

        summaries.append(summary)

    return summaries

CATEGORY_KOREAN = {
    'POP': '강수 확률 (%)',
    'PTY': '강수 형태',
    'PCP': '1시간 강수량 (mm)',
    'REH': '습도 (%)',
    'SNO': '1시간 신적설 (cm)',
    'SKY': '하늘 상태',
    'TMP': '1시간 기온 (℃)',
    'TMN': '일 최저 기온 (℃)',
    'TMX': '일 최고 기온 (℃)',
    'UUU': '풍속 (동서 성분) (m/s)',
    'VVV': '풍속 (남북 성분) (m/s)',
    'WAV': '파고 (M)',
    'VEC': '풍향 (deg)',
    'WSD': '풍속 (m/s)'
}

def format_weather_summaries(summaries):

    text_list = []

    for s in summaries:

        category_korean = CATEGORY_KOREAN.get(s['category'], s['category'])

        line = f"{s['fcstDate']} {s['fcstTime']} | {category_korean} : {s['fcstValue']}"

        text_list.append(line)

    text = "\n".join(text_list)

    return text