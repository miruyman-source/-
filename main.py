import streamlit as st
import pandas as pd

# ----------------------------
# 기본 설정
# ----------------------------
st.set_page_config(page_title="서울-양평 열섬 & 전력수요 분석", layout="wide")
st.title("🌡️ 도시 열섬현상과 전력수요 분석")
st.caption("2025년 시간별 데이터를 이용해 서울-양평 온도차(열섬)와, 기온-전력수요 관계를 살펴봅니다.")


# ----------------------------
# 데이터 불러오기
# ----------------------------
@st.cache_data
def load_temp_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

    for df in (seoul, yangpyeong):
        df["일시"] = pd.to_datetime(df["일시"])

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


@st.cache_data
def load_power_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    power["일시"] = pd.to_datetime(power["일시"])

    merged = pd.merge(
        seoul[["일시", "기온(°C)"]],
        power[["일시", "전력수요(MWh)"]],
        on="일시",
    )
    merged["월"] = merged["일시"].dt.month

    return merged


try:
    temp_data = load_temp_data()
except FileNotFoundError:
    st.error("'서울_기온.csv' 또는 '양평_기온.csv' 파일을 찾을 수 없습니다. 같은 폴더에 있는지 확인해주세요.")
    st.stop()

try:
    power_data = load_power_data()
except FileNotFoundError:
    st.error("'서울_기온.csv' 또는 '전력수요.csv' 파일을 찾을 수 없습니다. 같은 폴더에 있는지 확인해주세요.")
    st.stop()


# ----------------------------
# 탭 구성
# ----------------------------
tab1, tab2 = st.tabs(["🏙️ 열섬 분석", "⚡ 전력 연결"])


# ============================================================
# 탭1: 열섬 분석
# ============================================================
with tab1:
    st.header("① 1년간 서울-양평 기온 변화")
    st.line_chart(temp_data.set_index("일시")[["서울", "양평"]])

    st.markdown("---")

    st.header("② 시각별 평균 기온차 (서울 - 양평)")
    hourly_diff = temp_data.groupby("시각")["차이(서울-양평)"].mean()
    st.bar_chart(hourly_diff)
    st.caption("값이 0보다 크면 서울이 양평보다 더 더웠다는 뜻입니다. "
               "일반적으로 야간~새벽 시간대에 열섬현상이 두드러지는 경향이 있습니다.")

    st.markdown("---")

    st.header("③ 월별 평균 기온차 (서울 - 양평)")
    monthly_diff = temp_data.groupby("월")["차이(서울-양평)"].mean()
    st.bar_chart(monthly_diff)
    st.caption("계절에 따라 열섬현상의 크기가 어떻게 달라지는지 확인할 수 있습니다.")

    st.markdown("---")
    st.subheader("📊 요약 통계")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 기온차 (서울-양평)", f"{temp_data['차이(서울-양평)'].mean():.2f} °C")
    col2.metric("최대 기온차", f"{temp_data['차이(서울-양평)'].max():.2f} °C")
    col3.metric("최소 기온차", f"{temp_data['차이(서울-양평)'].min():.2f} °C")

    with st.expander("원본 데이터 미리보기"):
        st.dataframe(temp_data.head(50))


# ============================================================
# 탭2: 전력 연결
# ============================================================
with tab2:
    st.header("① 기온과 전력수요의 관계 (산점도)")
    st.scatter_chart(power_data, x="기온(°C)", y="전력수요(MWh)")
    st.caption("가로축: 서울 기온(°C), 세로축: 전력수요(MWh)")

    st.markdown("---")

    st.header("② 기온 구간별 평균 전력수요")

    # 기온을 5도 단위 구간으로 나누기
    min_temp = power_data["기온(°C)"].min()
    max_temp = power_data["기온(°C)"].max()
    bin_start = (min_temp // 5) * 5
    bin_end = (max_temp // 5 + 1) * 5
    bins = list(range(int(bin_start), int(bin_end) + 5, 5))

    power_data["기온구간"] = pd.cut(power_data["기온(°C)"], bins=bins)
    temp_bin_power = power_data.groupby("기온구간", observed=True)["전력수요(MWh)"].mean()
    temp_bin_power.index = temp_bin_power.index.astype(str)
    st.bar_chart(temp_bin_power)
    st.caption("기온 구간(°C)별 평균 전력수요입니다. 보통 한여름·한겨울처럼 기온이 극단적일수록 전력수요가 높아지는 U자형 패턴이 나타납니다.")

    st.markdown("---")

    st.header("③ 월별 평균 전력수요")
    monthly_power = power_data.groupby("월")["전력수요(MWh)"].mean()
    st.bar_chart(monthly_power)

    st.markdown("---")
    st.subheader("📊 요약 통계")
    col1, col2, col3 = st.columns(3)
    col1.metric("평균 전력수요", f"{power_data['전력수요(MWh)'].mean():.0f} MWh")
    col2.metric("최대 전력수요", f"{power_data['전력수요(MWh)'].max():.0f} MWh")
    col3.metric("최소 전력수요", f"{power_data['전력수요(MWh)'].min():.0f} MWh")

    with st.expander("원본 데이터 미리보기"):
        st.dataframe(power_data.head(50))
