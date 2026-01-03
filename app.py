import streamlit as st
import pandas as pd


def calculate_score(row, preference):
    score = 0

    if preference == "금리 중시":
        score += row["금리(%)"] * 2
        score += 1 if row["상품유형"] == "적금" else 0

    elif preference == "기간 중시":
        score += row["금리(%)"]
        if row["기간(개월)"] <= 6:
            score += 3
        elif row["기간(개월)"] <= 12:
            score += 2

    elif preference == "적금 선호":
        score += row["금리(%)"]
        score += 3 if row["상품유형"] == "적금" else 0

    return round(score, 2)



# -------------------------
# 1. 페이지 설정
# -------------------------
st.set_page_config(
    page_title="예·적금 금리 비교",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 예·적금 금리 비교 서비스")
st.write("은행별 예·적금 상품을 한눈에 비교할 수 있습니다.")

# -------------------------
# 2. 데이터 불러오기
# -------------------------
df = pd.read_csv("deposit_data.csv")


# -------------------------
# 3. 사이드바 필터
# -------------------------
st.sidebar.header("🔍 상품 찾기")

product_type = st.sidebar.selectbox(
    "상품 유형",
    options=["전체", "예금", "적금"]
)

bank = st.sidebar.multiselect(
    "은행 선택",
    options=df["은행"].unique(),
    default=df["은행"].unique()
)

period = st.sidebar.selectbox(
    "가입 기간(개월)",
    options=["전체"] + sorted(df["기간(개월)"].unique().tolist())
)

rate_range = st.sidebar.slider(
    "금리 범위 (%)",
    min_value=float(df["금리(%)"].min()),
    max_value=float(df["금리(%)"].max()),
    value=(float(df["금리(%)"].min()), float(df["금리(%)"].max())),
    step=0.1
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 추천 기준")

preference = st.sidebar.radio(
    "어떤 기준을 더 중요하게 볼까요?",
    ["금리 중시", "기간 중시", "적금 선호"]
)



# -------------------------
# 4. 필터링 로직
# -------------------------
filtered_df = df.copy()

if product_type != "전체":
    filtered_df = filtered_df[filtered_df["상품유형"] == product_type]

filtered_df = filtered_df[filtered_df["은행"].isin(bank)]

if period != "전체":
    filtered_df = filtered_df[filtered_df["기간(개월)"] == period]

filtered_df = filtered_df[
    (filtered_df["금리(%)"] >= rate_range[0]) &
    (filtered_df["금리(%)"] <= rate_range[1])
]

filtered_df["추천점수"] = filtered_df.apply(
    lambda row: calculate_score(row, preference),
    axis=1
)

# 추천 점수 기준 정렬
filtered_df = filtered_df.sort_values(by="추천점수", ascending=False)

# -------------------------
# 6. 결과 출력
# -------------------------
st.subheader("📊 상품 비교 결과")
st.dataframe(filtered_df, use_container_width=True)


st.subheader("🏦 은행별 평균 금리")

avg_rate_by_bank = (
    filtered_df
    .groupby("은행")["금리(%)"]
    .mean()
    .reset_index()
)

st.bar_chart(avg_rate_by_bank.set_index("은행"))


st.subheader("📈 예금 vs 적금 평균 금리")

avg_rate_by_type = (
    filtered_df
    .groupby("상품유형")["금리(%)"]
    .mean()
    .reset_index()
)

st.bar_chart(avg_rate_by_type.set_index("상품유형"))


# -------------------------
# 7. 최고 금리 상품 강조
# -------------------------
if not filtered_df.empty:
    top = filtered_df.iloc[0]
    st.markdown("## 🏆 오늘의 추천 상품")

    col1, col2, col3 = st.columns(3)

    col1.metric("은행", top["은행"])
    col2.metric("상품명", top["상품명"])
    col3.metric("금리", f"{top['금리(%)']} %")

    st.info(
        f"""
        🔍 **추천 이유**
        - 선택 기준: **{preference}**
        - 가입 기간: {top['기간(개월)']}개월
        - 상품 유형: {top['상품유형']}
        - 추천 점수: {top['추천점수']}
        """
    )
else:
    st.warning("조건에 맞는 상품이 없습니다.")
    