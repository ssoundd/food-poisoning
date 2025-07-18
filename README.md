# 식중독 리스크 실시간 모니터링 시스템

기상청 단기 예보 + 과거 식중독 발생 이력, 최신 예측 지수를 종합 분석하여 **지역별 식중독 위험도를 실시간 평가**하고, **대응 가이드**를 제공합니다.

> **목표 :**\
> 국민 건강 보호를 위한 데이터 기반 조기 경보 시스템

---

## 주요 기능

- **위치 기반 날씨 정보 수집**\
  → 기상청 API
- **식중독 발생 이력 분석**\
  → 식품의약품안전처 OpenAPI + VECTOR DB 구축
- **최신 식중독 예측 지수 자동 수집**\
  → Selenium 기반 웹 크롤링 및 정제
- **LangChain 기반 지능형 질의 응답**\
  → GPT-4o 연동, 다중 소스 통합 질의
- **웹 대시 보드 시각화**\
  → Streamlit 기반 UI + Plotly 시각화 + 요약 카드
- **유사도 기반 검색**\
  → Chroma + OpenAI `text-embedding-3-large`

---

## 시스템 구성도

```plaintext
[사용자 질의]
    ↓
[날씨 API] + [식중독 이력 VECTOR DB] + [예측 지수]
    ↓
[LangChain Chain] → GPT-4o 기반 응답 생성
    ↓
[Streamlit 대시 보드 출력]
```

---

## 설치 및 실행

### 1. 환경 설정

```bash
pip install -r requirements.txt
```

### 2. .env 파일 생성

```env
OPENAI_API_KEY
WEATHER_API_KEY
SITOTOXISM_API_KEY
```

### 3. 실행

```bash
streamlit run app.py
```

---

## 파일 구조

```plaintext
📁 파일
.
├── app.py                     # Streamlit 메인 앱
├── main.py                    # LLM 체인, 질의 처리 메인 로직
├── weather_main.py            # 기상청 API 처리 모듈
├── predict_main.py            # 식중독 예측 지수 크롤링/정제
├── sitotoxism_main.py         # 식중독 이력 VECTOR DB 업데이트
├── sitotoxism_data_loader.py
├── sitotoxism_doc_converter.py
├── sitotoxism_chroma_updater.py
├── summary_card.py            # 사이드바 요약 카드
├── .env                       # API 키 환경 변수
├── requirements.txt
```

---

## 기술 스택

Frontend : Streamlit

LLM Chain : LangChain + GPT-4o (OpenAI)

Vector DB : Chroma + text-embedding-3-large

크롤링 : Selenium

API : 기상청, 식품의약품안전처

시각화 : Plotly Express

---

## 활용 시나리오

- 특정 지역에서 **식중독 발생 위험이 높은 시기 파악**
- **날씨 조건 변화**에 따른 실시간 위험도 반영
- 사용자의 위치 기반 **즉시 대응 가이드 제공**
- 과거 유사 패턴 분석을 통한 **사전 예방**