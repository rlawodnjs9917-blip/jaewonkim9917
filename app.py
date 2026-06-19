import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

# =========================
# 설정
# =========================
st.set_page_config(
    page_title="조선소 블록 생산 분석",
    page_icon="🚢",
    layout="wide"
)

DATA_FILE = "block_data.csv"

# =========================
# 데이터 로드
# =========================
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["블록명", "공정", "작업시간"])

# 블록 자동 번호 생성
if len(df) > 0:
    last_num = int(df["블록명"].str.replace("B", "").max())
else:
    last_num = 100

# =========================
# 타이틀
# =========================
st.title("🚢 조선소 블록 생산 공정 분석 시스템")

st.markdown("블록 생산 공정별 작업량을 분석하여 병목 공정을 시각화합니다.")

st.divider()

# =========================
# 입력
# =========================
st.header("📌 작업 입력")

col1, col2 = st.columns(2)

with col1:
    process = st.selectbox(
        "공정",
        ["절단", "용접", "조립", "도장", "탑재"]
    )

with col2:
    work_time = st.number_input("작업시간 (시간)", min_value=1, value=1)

if st.button("➕ 등록"):

    new_block = f"B{last_num + 1}"

    new_row = pd.DataFrame([{
        "블록명": new_block,
        "공정": process,
        "작업시간": work_time
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    st.success(f"{new_block} 등록 완료!")

st.divider()

# =========================
# 데이터 보기
# =========================
st.header("📊 생산 데이터")

st.dataframe(df, use_container_width=True)

st.divider()

# =========================
# 분석
# =========================
if len(df) > 0:

    process_df = df.groupby("공정")["작업시간"].sum().reset_index()

    total = process_df["작업시간"].sum()

    bottleneck = process_df.loc[
        process_df["작업시간"].idxmax(),
        "공정"
    ]

    # KPI
    st.header("📌 핵심 지표")

    c1, c2, c3 = st.columns(3)

    c1.metric("총 작업시간", f"{total} hr")
    c2.metric("공정 수", len(process_df))
    c3.metric("병목 공정", bottleneck)

    st.divider()

    # =========================
    # 막대 그래프
    # =========================
    st.header("📊 공정별 작업량")

    fig = px.bar(
        process_df,
        x="공정",
        y="작업시간",
        color="공정",
        text="작업시간",
        title="공정별 작업 부하"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # =========================
    # 파이차트
    # =========================
    st.header("🥧 공정 비율")

    pie = px.pie(
        process_df,
        names="공정",
        values="작업시간",
        hole=0.4
    )

    st.plotly_chart(pie, use_container_width=True)

# =========================
# 다운로드
# =========================
st.header("💾 다운로드")

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "⬇ CSV 다운로드",
    csv,
    "block_data.csv",
    "text/csv"
)

output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="블록생산데이터")

excel_data = output.getvalue()

st.download_button(
    "⬇ Excel 다운로드",
    excel_data,
    "block_data.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

# =========================
# 초기화
# =========================
if st.button("🗑 전체 초기화"):
    df = pd.DataFrame(columns=["블록명", "공정", "작업시간"])
    df.to_csv(DATA_FILE, index=False)
    st.success("초기화 완료")
    st.rerun()