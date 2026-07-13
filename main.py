import streamlit as st
import pandas as pd

st.set_page_config(page_title="서울-양평 열섬 & 전력 분석", layout="wide")
st.title("🌡️ 서울·양평 열섬 현상 & 전력수요 분석")

# ------------------------------
# 데이터 불러오기
# ------------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
    power["일시"] = pd.to_datetime(power["일시"])

    seoul = seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울_기온"})
    yangpyeong = yangpyeong[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평_기온"})

    return seoul, yangpyeong, power

seoul, yangpyeong, power = load_data()

# ------------------------------
# 탭 구성
# ------------------------------
tab1, tab2 = st.tabs(["🏙️ 열섬 분석", "⚡ 전력 연결"])

# ==============================
# 탭 1: 열섬 분석
# ==============================
with tab1:
    st.header("서울 vs 양평 기온 비교 (열섬 현상)")

    # 같은 일시끼리 병합
    merged = pd.merge(seoul, yangpyeong, on="일시", how="inner")
    merged["기온차(서울-양평)"] = merged["서울_기온"] - merged["양평_기온"]
    merged["시각"] = merged["일시"].dt.hour
    merged["월"] = merged["일시"].dt.month

    # ① 1년간 두 지역 기온 변화
    st.subheader("① 1년간 두 지역 기온 변화")
    chart1 = merged.set_index("일시")[["서울_기온", "양평_기온"]]
    st.line_chart(chart1)

    # ② 시각별 평균 기온차
    st.subheader("② 시각(0~23시)별 평균 기온차 (서울-양평)")
    hourly_diff = merged.groupby("시각")["기온차(서울-양평)"].mean()
    st.bar_chart(hourly_diff)

    # ③ 월별 평균 기온차
    st.subheader("③ 월(1~12월)별 평균 기온차 (서울-양평)")
    monthly_diff = merged.groupby("월")["기온차(서울-양평)"].mean()
    st.bar_chart(monthly_diff)

# ==============================
# 탭 2: 전력 연결
# ==============================
with tab2:
    st.header("서울 기온과 전력수요의 관계")

    # 같은 일시끼리 병합
    merged_power = pd.merge(seoul, power, on="일시", how="inner")
    merged_power["월"] = merged_power["일시"].dt.month

    # ① 기온 vs 전력수요 산점도
    st.subheader("① 기온(가로) - 전력수요(세로) 산점도")
    st.scatter_chart(
        merged_power,
        x="서울_기온",
        y="전력수요(MWh)",
    )

    # ② 기온 구간별 평균 전력수요
    st.subheader("② 기온 구간별 평균 전력수요")
    min_t = merged_power["서울_기온"].min()
    max_t = merged_power["서울_기온"].max()
    bins = list(range(int(min_t) - (int(min_t) % 5), int(max_t) + 6, 5))
    labels = [f"{b}~{b+5}°C" for b in bins[:-1]]
    merged_power["기온구간"] = pd.cut(
        merged_power["서울_기온"], bins=bins, labels=labels, right=False
    )
    temp_bin_power = merged_power.groupby("기온구간", observed=True)["전력수요(MWh)"].mean()
    st.bar_chart(temp_bin_power)

    # ③ 월별 평균 전력수요
    st.subheader("③ 월(1~12월)별 평균 전력수요")
    monthly_power = merged_power.groupby("월")["전력수요(MWh)"].mean()
    st.bar_chart(monthly_power)
