from dotenv import load_dotenv
import os
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from sitotoxism_main import update_sitotoxism, load_sitotoxism_chroma
from weather_main import fetch_weather_data, extract_weather_fields, format_weather_summaries
from predict_main import download_excel, get_excel_file, read_excel_file
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

os.makedirs("cache", exist_ok = True)

set_llm_cache(SQLiteCache(database_path = "cache/sqlite_cache.db"))

# ----------- Step 1 : SITOTOXISM VS ----------- #

# update_sitotoxism()

# sitotoxism_vs = load_sitotoxism_chroma()

# ----------- Step 2 : WEATHER API ----------- #

def prepare_weather_data(query):
    
    weather = fetch_weather_data(query)

    summaries = extract_weather_fields(weather)

    weather_text = format_weather_summaries(summaries)

    return weather_text

# ----------- Step 3 : Download & Read PREDICT ----------- #

def prepare_predict_data():
    
    download_path = os.path.abspath("download")

    download_excel(download_path)

    file_path = get_excel_file(download_path)

    predict_df = read_excel_file(file_path)

    predict_md = predict_df.to_markdown(index = False)

    return predict_df, predict_md

# ----------- Step 4 : CHAIN ----------- #

def create_chain():

    llm = ChatOpenAI(model = "gpt-4o", streaming = True)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
         당신은 식중독 위험을 예측하는 **공공 보건 전문가**입니다. 당신의 임무는 다음 세 가지 데이터를 종합적으로 분석하여, 사용자의 질문에 **논리적이고 실질적인 인사이트**를 제공하는 것입니다.

         1. [날씨 데이터] : 지금 이 시간부터 3일 간 단기 예보 기준의 지역별 기상 상태
         2. [과거 데이터] : 과거 식중독 발생 지역, 원인 시설, 원인 바이러스별 발생 건수와 환자 수
         3. [예측 데이터] : 지역별 식중독 예측 지수와 단계

         당신의 응답은 아래 사항을 반드시 포함해야 합니다. :
         - **정보 간의 연관성 또는 인과 관계 해석** (예 : 고온 다습한 날씨 → 세균성 식중독 증가 등)
         - **과거 사례와 현재/예측 데이터를 수치 기반으로 정량적 비교** (예 : 최근 3년 간 주된 원인 바이러스/시설에 따른 평균 발생 건수 및 환자 수 비교 등)
         - **위험 단계에 따른 주의/예방 조치 제안**
         - **각 위험 요소(바이러스, 시설, 지역)의 발생 건수 및 환자 수**를 반드시 제시하고, 예측 데이터와 관련성을 설명

         모호한 해석이나 일반적인 설명은 피하고, 사용자가 **지금 위치에서 실제로 도움이 될 수 있는 정보**를 제공해 주세요.
         """),
        MessagesPlaceholder(variable_name = 'history'),
        ("human", "[날씨 정보]\n{weather_data}\n\n[과거 정보]\n{past_data}\n\n[예측 정보]\n{predict_data}\n\n질문 :\n{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    return chain

# ----------- Step 5 : ANSWER ----------- #

def get_answer(sitotoxism_vs, query, chain, weather_text, predict_md, history):

    retriever = sitotoxism_vs.as_retriever()

    retriever_docs = retriever.invoke(query)

    reference = "\n\n".join([doc.page_content for doc in retriever_docs])

    answer = chain.stream({"weather_data" : weather_text, "past_data" : reference, "predict_data" : predict_md, "question" : query, 'history' : history})

    return answer

if __name__ == "__main__":

    query = input("위치와 함께 질문을 입력하세요.")

    update_sitotoxism()
    sitotoxism_vs = load_sitotoxism_chroma()

    weather_text = prepare_weather_data(query)

    predict_md = prepare_predict_data()

    chain = create_chain()

    history = []

    answer = get_answer(sitotoxism_vs, query, chain, weather_text, predict_md, history)

    for chunk in answer:
        print(chunk, end = '', flush = True)