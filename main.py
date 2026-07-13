import streamlit as st
import pandas as pd

# ----------------------------
# 기본 설정
# ----------------------------
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")
st.title("🌡️ 서울 vs 양평 기온 비교로 보는 도시 열섬현상")
st.caption("2025년 시간별 기온 데이터를 이용해 서울(도심)과 양평(비도심)의 온도차를 살펴봅니다.")


# ----------------------------
# 데이터 불러오기
# ----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

    for df in (seoul, yangpyeong):
        df["일시"] = pd.to_datetime(df["일시"])

    # 서울, 양평 데이터를 일시 기준으로 병합
    merged = pd.merge(
        seoul[["일시", "기온(°C)"]],
        yangpyeong[["일시", "기온(°C)"]],
        on="일시",
        suffixes=("_서울", "_양평"),
    )
    merged = merged.rename(
        columns={"기온(°C)_서울": "서울", "기온(°C)_양평": "양평"}
    )
    merged["차이(서울-양평)"] = merged["서울"] - merged["양평"]
    merged["시각"] = merged["일시"].dt.hour
    merged["월"] = merged["일시"].dt.month

    return merged


try:
    data = load_data()
except FileNotFoundError as e:
    st.error(
        "데이터 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 "
        "이 앱과 같은 폴더에 있는지 확인해주세요."
    )
    st.stop()


# ----------------------------
# ① 1년간 두 지역의 기온 변화 (선그래프)
# ----------------------------
st.header("① 1년간 서울-양평 기온 변화")
st.line_chart(data.set_index("일시")[["서울", "양평"]])

st.markdown("---")


# ----------------------------
# ② 시각(0~23시)별 평균 기온차 (막대그래프)
# ----------------------------
st.header("② 시각별 평균 기온차 (서울 - 양평)")

hourly_diff = data.groupby("시각")["차이(서울-양평)"].mean()
st.bar_chart(hourly_diff)

st.caption("값이 0보다 크면 서울이 양평보다 더 더웠다는 뜻입니다. "
           "일반적으로 야간~새벽 시간대에 열섬현상이 두드러지는 경향이 있습니다.")

st.markdown("---")


# ----------------------------
# ③ 월(1~12월)별 평균 기온차 (막대그래프)
# ----------------------------
st.header("③ 월별 평균 기온차 (서울 - 양평)")

monthly_diff = data.groupby("월")["차이(서울-양평)"].mean()
st.bar_chart(monthly_diff)

st.caption("계절에 따라 열섬현상의 크기가 어떻게 달라지는지 확인할 수 있습니다.")

st.markdown("---")


# ----------------------------
# 요약 통계
# ----------------------------
st.header("📊 요약 통계")

col1, col2, col3 = st.columns(3)
col1.metric("평균 기온차 (서울-양평)", f"{data['차이(서울-양평)'].mean():.2f} °C")
col2.metric("최대 기온차", f"{data['차이(서울-양평)'].max():.2f} °C")
col3.metric("최소 기온차", f"{data['차이(서울-양평)'].min():.2f} °C")

with st.expander("원본 데이터 미리보기"):
    st.dataframe(data.head(50))
