# ============================================================
#  기온과 전력으로 보는 도시 열섬현상
#  탭1) 열섬 분석 (서울 vs 양평)   탭2) 전력 연결 (기온 vs 전력)
#  데이터: 기상청 시간별 기온(서울/양평) + 전력거래소 시간별 전국 전력수요 (2025년)
# ============================================================
import streamlit as st
import pandas as pd

st.set_page_config(page_title="열섬과 전력", layout="wide")

# ---------- 데이터 불러오기 (한글 파일이라 encoding 지정!) ----------
seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
yang = pd.read_csv("양평_기온.csv", encoding="cp949")
power = pd.read_csv("전력수요.csv", encoding="cp949")

# ---------- 데이터 정리하기 ----------
for df in (seoul, yang):
    df.columns = ["지점", "지점명", "일시", "기온"]
    df["일시"] = pd.to_datetime(df["일시"])
power.columns = ["일시", "전력수요"]
power["일시"] = pd.to_datetime(power["일시"])

st.title("🌡️⚡ 기온과 전력으로 보는 도시 열섬현상")
st.write("서울과 양평의 기온을 비교해 **열섬현상**을 찾고, 기온과 전력의 관계로 그 **되먹임**까지 살펴봅니다.")

tab1, tab2 = st.tabs(["🌡️ 탭1. 열섬 분석 (서울 vs 양평)", "⚡ 탭2. 전력 연결 (기온 vs 전력)"])

# ============================================================
#  탭 1 — 열섬 분석
# ============================================================
with tab1:
    heat = pd.merge(
        seoul[["일시", "기온"]], yang[["일시", "기온"]],
        on="일시", suffixes=("_서울", "_양평"),
    ).rename(columns={"기온_서울": "서울", "기온_양평": "양평"})
    heat["기온차"] = heat["서울"] - heat["양평"]      # 서울 - 양평
    heat["시각"] = heat["일시"].dt.hour
    heat["월"] = heat["일시"].dt.month

    c1, c2, c3 = st.columns(3)
    c1.metric("서울 평균기온", f"{heat['서울'].mean():.1f} °C")
    c2.metric("양평 평균기온", f"{heat['양평'].mean():.1f} °C")
    c3.metric("평균 기온차 (서울-양평)", f"{heat['기온차'].mean():+.2f} °C")

    st.subheader("① 1년간 두 지역의 기온 변화")
    st.line_chart(heat.set_index("일시")[["서울", "양평"]])
    st.caption("여름에 높고 겨울에 낮은 큰 흐름. 서울이 대체로 조금 더 높다.")

    st.subheader("② 시각별 평균 기온차 (서울 − 양평)")
    hourly = heat.groupby("시각")["기온차"].mean()
    st.bar_chart(hourly)
    st.caption("새벽에 차이가 크고 낮에는 작다 → 도시는 '밤에 잘 식지 않는다' (열섬현상!)")

    st.subheader("③ 월별 평균 기온차 (서울 − 양평)")
    monthly = heat.groupby("월")["기온차"].mean()
    st.bar_chart(monthly)
    st.caption("여름(특히 7월)에 기온차가 크다 → 열섬은 여름에 더 심하다.")

# ============================================================
#  탭 2 — 전력 연결
# ============================================================
with tab2:
    pw = pd.merge(seoul[["일시", "기온"]], power[["일시", "전력수요"]], on="일시")
    pw["월"] = pw["일시"].dt.month

    c1, c2, c3 = st.columns(3)
    c1.metric("평균 기온", f"{pw['기온'].mean():.1f} °C")
    c2.metric("평균 전력수요", f"{pw['전력수요'].mean():,.0f} MWh")
    c3.metric("기온-전력 상관", f"{pw['기온'].corr(pw['전력수요']):.2f}")

    st.subheader("① 기온이 오르면 전력 사용도 늘어날까? (산점도)")
    st.scatter_chart(pw, x="기온", y="전력수요")
    st.caption("점 하나가 한 시간. 쾌적할 땐 적게, 덥거나 추우면 많이 쓴다 (U자·나이키 모양).")

    st.subheader("② 기온 구간별 평균 전력수요")
    pw = pw.copy()
    pw["기온구간"] = (pw["기온"] // 5 * 5).astype(int)
    st.bar_chart(pw.groupby("기온구간")["전력수요"].mean())
    st.caption("가장 쾌적한 기온에서 전력이 가장 적고, 덥거나 추우면 늘어난다 — 냉방과 난방!")

    st.subheader("③ 월별 평균 전력수요")
    st.bar_chart(pw.groupby("월")["전력수요"].mean())
    st.caption("여름(냉방)과 겨울(난방)에 봉우리. 열섬이 심한 여름 = 전력을 많이 쓰는 여름!")

    st.subheader("④ 시각별 평균 전력수요")
    pw["시각"] = pw["일시"].dt.hour
    st.line_chart(pw.groupby("시각")["전력수요"].mean())
    st.caption("전국 전력은 낮·저녁에 높고 새벽에 낮다(생활 리듬). "
               "그런데 열섬(탭1 ②)은 새벽에 심했다 — 왜 다를까? 토론해 보자!")

# ---------- 마무리 질문 ----------
st.divider()
st.info("💬 **생각해 보기** — 도시는 밤에 잘 식지 않아 더 덥습니다(열섬). "
        "더우면 냉방을 켜고, 실외기는 다시 열을 내뿜죠. "
        "두 탭의 그래프를 근거로 '더위 → 냉방 → 더 큰 더위'의 고리를 설명해 봅시다.")
