import streamlit as st
import uuid
from main import update_sitotoxism, load_sitotoxism_chroma, prepare_weather_data, prepare_predict_data, create_chain, get_answer
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from summary_card import get_summary_card
import plotly.express as px
from langchain_core.messages import AIMessage, HumanMessage

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

if "sitotoxism_vs" not in st.session_state:
    with st.spinner("페이지 로딩 중 ..."):
        update_sitotoxism()
        st.session_state.sitotoxism_vs = load_sitotoxism_chroma()

if "predict_df" not in st.session_state:
    predict_df, predict_md = prepare_predict_data()
    st.session_state.predict_df = predict_df

if "chain" not in st.session_state:
    st.session_state.chain = create_chain()

if "all_memory" not in st.session_state:
    st.session_state.all_memory = {}

if session_id not in st.session_state.all_memory:
    st.session_state.all_memory[session_id] = ConversationBufferMemory(return_messages = True)

user_memory = st.session_state.all_memory[session_id]

st.set_page_config(page_title = "식중독 리스크 실시간 모니터링 시스템", page_icon = "🩺", layout = "wide")

st.markdown("# 식중독 리스크 실시간 모니터링 시스템")
st.markdown(
    """
    위치와 함께 식중독 관련 질문을 입력하면, 해당 지역의 **날씨 상황, 과거 발생 기록, 예측 지수**를 기반으로  
    종합적인 **위험 평가 및 대응 가이드**를 제안합니다.
    """
)
st.caption(f"🕝 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.sidebar:

    if "summary_card" not in st.session_state:
        st.session_state.summary_card = get_summary_card()

    summary = st.session_state.summary_card

    st.subheader(f"최근 3년 간 통계 ({summary['current_month']}월)")
    st.markdown(f"""
        <div style = 'background-color : #B2BEB5; padding : 16px; border-radius : 10px; line-height : 1.8; color : #013220;'>
            >>  <strong>평균 발생 건수</strong> : <span style = 'color : #145A32'>{summary['avg_cnt']}건</span>
            <br>
            >>  <strong>평균 환자 수</strong> : <span style = 'color : #145A32'>{summary['avg_patients']}명</span>
            <br>
            >>  <strong>최다 원인 바이러스</strong> : <span style = 'color : #145A32'>{summary['top_virus_name']} ({summary['top_virus_count']}명)</span>
            <br>
            >>  <strong>최다 원인 시설</strong> : <span style = 'color : #145A32'>{summary['top_facility_name']} ({summary['top_facility_count']}명)</span>
        </div>
        """,
        unsafe_allow_html = True)
    
    st.divider()

    st.subheader("식중독 예측 리포트")
    st.subheader(datetime.now().strftime('%Y-%m-%d (%a)'))

    predict_df = st.session_state.predict_df

    actual_시도_list = predict_df['시도'].dropna().unique().tolist()
    시도_list = ["시/도 선택"] + sorted(actual_시도_list)
    select_시도 = st.selectbox("시/도", options = 시도_list, index = 0, key = "selected_province")

    if st.session_state.get("last_province") != st.session_state.selected_province:
        st.session_state.pop("조회_결과", None)
        st.session_state["last_province"] = st.session_state.selected_province
        st.session_state["last_city"] = None

    if select_시도 != "시/도 선택":

        filter_df = predict_df[predict_df['시도'] == select_시도]

        actual_시군구_list = filter_df['시군구'].dropna().unique().tolist()
        시군구_list = ["시/군/구 선택"] + sorted(actual_시군구_list)
        select_시군구 = st.selectbox("시/군/구", options = 시군구_list, index = 0, key = "selected_city")

        if st.session_state.get("last_city") != st.session_state.selected_city:
            st.session_state.pop("조회_결과", None)
            st.session_state["last_city"] = st.session_state.selected_city

        if select_시군구 != "시/군/구 선택":

            result = predict_df[(predict_df['시도'] == select_시도) & (predict_df['시군구'] == select_시군구)][['식중독_예측지수', '단계']]

            if st.button("조회"):

                if not result.empty:
                    st.session_state['조회_결과'] = {
                        '지수' : result.iloc[0]['식중독_예측지수'],
                        '단계' : result.iloc[0]['단계']
                    }

                else:
                    st.error("⚠️ 선택하신 지역에 대한 예측 정보가 아직 준비되지 않았습니다.")

    if '조회_결과' in st.session_state:

        지수 = st.session_state['조회_결과']['지수']
        단계 = st.session_state['조회_결과']['단계']

        st.markdown(
            f"""
            <div style = 'padding : 10px; background-color : #f0ebf8; border-radius : 8px;'>
                ✔️ <strong>지수</strong> : {지수}
                <br>
                ✔️ <strong>단계</strong> : {단계}
            </div>
            """,
            unsafe_allow_html = True
        )

        if 단계 == "심각":
            st.warning("🔴 심각 단계입니다. 위생 관리 및 음식물 보관에 각별히 주의하세요.")
        elif 단계 == "경고":
            st.info("🟠 경고 단계입니다. 식중독 예방 수칙을 철저히 준수하세요.")
        elif 단계 == "주의":
            st.info("🟡 주의 단계입니다. 위생 상태를 점검하고, 예방 수칙을 숙지하세요.")
        elif 단계 == "관심":
            st.success("🟢 관심 단계입니다. 현재 위험 요소는 낮지만, 기본 위생 수칙은 계속 지켜 주세요.")
        else:
            st.error(f"⚠️ 유효하지 않은 단계입니다. 처리할 수 없습니다.")

st.divider()

with st.expander(f"📊 {datetime.now().strftime('%Y-%m-%d (%a)')} 식중독 예측 지수 및 단계 그래프", expanded = True):

    predict_df = st.session_state.predict_df

    시도_선택 = st.selectbox("시/도", ["전체"] + sorted(predict_df['시도'].dropna().unique().tolist()))

    if 시도_선택 == "전체":

        grouped = predict_df.groupby("시도")["식중독_예측지수"].mean().reset_index()

        fig = px.bar(
            grouped,
            x = '시도',
            y = '식중독_예측지수',
            title = '시/도 평균 예측 지수',
            labels = {'식중독_예측지수' : '예측 지수', '시도' : '시/도'},
            height = 450,
            color_discrete_sequence = ["#91A3B0"]
        )

        st.plotly_chart(fig, use_container_width = True)

    else:

        filter_df = predict_df[predict_df['시도'] == 시도_선택]

        시군구_선택 = st.multiselect("시/군/구", sorted(filter_df['시군구'].dropna().unique().tolist()))
        단계_선택 = st.selectbox("예측 단계", ["전체"] + sorted(predict_df['단계'].dropna().unique().tolist()))

        if 시군구_선택:
            filter_df = filter_df[filter_df['시군구'].isin(시군구_선택)]

        if 단계_선택 != "전체":
            filter_df = filter_df[filter_df['단계'] == 단계_선택]

        if not filter_df.empty:

            fig = px.bar(
                filter_df,
                x = '시군구',
                y = '식중독_예측지수',
                color = '단계',
                title = '시/군/구 예측 지수',
                labels = {'식중독_예측지수' : '예측 지수', '시군구' : '시/군/구'},
                height = 450,
                color_discrete_map = {
                    "심각" : "#FF4B4B",
                    "경고" : "#FFA500",
                    "주의" : "#FFD700",
                    "관심" : "#00C851"
                }
            )

            fig.update_layout(xaxis_tickangle = -45)

            st.plotly_chart(fig, use_container_width = True)

        else:
            st.error("⚠️ 선택한 조건에 해당하는 데이터가 없습니다.")

for message in user_memory.chat_memory.messages:

    if isinstance(message, HumanMessage):
        with st.chat_message('user'):
            st.write(message.content)

    elif isinstance(message, AIMessage):
        with st.chat_message('assistant'):
            st.write(message.content)

if user_input := st.chat_input("예) 현재 서울특별시 강남구 식중독 발생 가능성은?"):

    with st.chat_message("user"):
        st.markdown(user_input)

    user_memory.chat_memory.add_user_message(user_input)

    history = user_memory.load_memory_variables({})["history"]

    with st.spinner("답변 생성 중 ..."):
        weather_text = prepare_weather_data(user_input)
        predict_df, predict_md = prepare_predict_data()

    with st.chat_message("assistant"):

        collect_chunk = []

        def stream_and_collect():
            for chunk in get_answer(st.session_state.sitotoxism_vs, user_input, st.session_state.chain, weather_text, predict_md, history):
                collect_chunk.append(chunk)
                yield chunk

        st.write_stream(stream_and_collect())

    response = "".join(collect_chunk)

    user_memory.chat_memory.add_ai_message(response)

    st.toast("결과가 제공되었습니다.", icon = "✔️")