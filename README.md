# 식중독 리스크 실시간 모니터링 시스템

기상청 단기 예보, 과거 식중독 발생 이력, 최신 예측 지수를 종합 분석하여 **지역별 식중독 위험도를 실시간 평가**하고, **대응 가이드**를 제공합니다.

## 주요 기능

- **위치 기반 날씨 데이터 수집** (기상청 API)
- **식중독 발생 이력 분석** (식품의약품안전처 OpenAPI)
- **최신 식중독 예측 지수 자동 크롤링**
- **LangChain 기반 다중 데이터 질의 응답**
- **Streamlit 웹 대시 보드** + 예측 지수 시각화 + 요약 카드
- **VECTOR DB 기반 유사도 검색** (Chroma + OpenAI Embedding)

## 시스템 구성도

[사용자 질의]
↓
[날씨 API] + [식중독 이력 벡터 DB] + [예측 지수]
↓
[LangChain Chain] → GPT-4o 기반 응답 생성
↓
[Streamlit 대시 보드 출력]

## 설치 및 실행

### 1. 환경 설정

pip install -r requirements.txt

### 2. .env 파일 생성

OPENAI_API_KEY
WEATHER_API_KEY
SITOTOXISM_API_KEY

### 3. 실행

streamlit run app.py

## 주요 파일 구조

<pre> ``` 📁 파일 ├── app.py # Streamlit 메인 앱 ├── main.py # LLM 체인, 질의 처리 메인 로직 ├── weather_main.py # 기상청 API 처리 모듈 ├── predict_main.py # 식중독 예측 지수 크롤링/정제 ├── sitotoxism_main.py # 식중독 이력 VECTOR DB 업데이트 ├── sitotoxism_data_loader.py ├── sitotoxism_doc_converter.py ├── sitotoxism_chroma_updater.py ├── summary_card.py # 사이드바 요약 카드 ├── .env # API 키 환경 변수 ├── requirements.txt ``` </pre>

## 기술 스택

Frontend : Streamlit

LLM Chain : LangChain + GPT-4o (OpenAI)

Vector DB : Chroma + text-embedding-3-large

크롤링 : Selenium

API 연동 : 기상청, 식품의약품안전처

데이터 시각화 : Plotly Express