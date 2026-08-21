import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="업무지원요청 데이터 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📊 업무지원요청 데이터 시각화 대시보드")
st.markdown("CSV 파일을 업로드하면 요청 현황, 긴급도, AI 활용구분 등을 자동으로 분석하여 대시보드로 시각화합니다.")

# 2. 파일 업로더
uploaded_file = st.file_uploader("📂 업무지원요청 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 한글 인코딩 대응 (utf-8, euc-kr)
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='euc-kr')

    # 날짜 데이터 변환
    if 'request_date' in df.columns:
        df['request_date'] = pd.to_datetime(df['request_date'])

    # 3. 사이드바 필터링
    st.sidebar.header("🔍 데이터 필터")

    categories = st.sidebar.multiselect(
        "카테고리 선택",
        options=df['category'].unique() if 'category' in df.columns else [],
        default=df['category'].unique() if 'category' in df.columns else []
    )

    urgencies = st.sidebar.multiselect(
        "긴급도 선택",
        options=df['urgency'].unique() if 'urgency' in df.columns else [],
        default=df['urgency'].unique() if 'urgency' in df.columns else []
    )

    statuses = st.sidebar.multiselect(
        "진행 상태 선택",
        options=df['status'].unique() if 'status' in df.columns else [],
        default=df['status'].unique() if 'status' in df.columns else []
    )

    ai_handlings = st.sidebar.multiselect(
        "AI 활용구분 선택",
        options=df['ai_handling'].unique() if 'ai_handling' in df.columns else [],
        default=df['ai_handling'].unique() if 'ai_handling' in df.columns else []
    )

    # 필터 적용
    filtered_df = df.copy()
    if categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    if urgencies:
        filtered_df = filtered_df[filtered_df['urgency'].isin(urgencies)]
    if statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(statuses)]
    if ai_handlings:
        filtered_df = filtered_df[filtered_df['ai_handling'].isin(ai_handlings)]

    # 4. 핵심 요약 지표 (KPI Cards)
    st.markdown("### 📌 핵심 요약 지표 (KPI)")
    col1, col2, col3, col4 = st.columns(4)

    total_requests = len(filtered_df)
    completed_requests = len(filtered_df[filtered_df['status'] == '완료']) if 'status' in filtered_df.columns else 0
    completion_rate = (completed_requests / total_requests * 100) if total_requests > 0 else 0
    high_urgency = len(filtered_df[filtered_df['urgency'] == '상']) if 'urgency' in filtered_df.columns else 0
    ai_available = len(filtered_df[filtered_df['ai_handling'] == '전용AI가능']) if 'ai_handling' in filtered_df.columns else 0

    col1.metric("총 요청 건수", f"{total_requests}건")
    col2.metric("처리 완료율", f"{completion_rate:.1f}%", f"{completed_requests}건 완료")
    col3.metric("긴급(상) 건수", f"{high_urgency}건")
    col4.metric("전용 AI 대응 가능", f"{ai_available}건")

    st.markdown("---")

    # 5. 시각화 차트 (Plotly)
    st.markdown("### 📈 현황 분석 차트")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        if 'category' in filtered_df.columns and not filtered_df.empty:
            cat_counts = filtered_df['category'].value_counts().reset_index()
            cat_counts.columns = ['category', 'count']
            fig1 = px.bar(
                cat_counts, x='category', y='count',
                title="카테고리별 요청 건수",
                color='category',
                text='count',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig1.update_layout(showlegend=False, xaxis_title="카테고리", yaxis_title="건수")
            st.plotly_chart(fig1, use_container_width=True)

    with row1_col2:
        if 'status' in filtered_df.columns and not filtered_df.empty:
            status_counts = filtered_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig2 = px.pie(
                status_counts, values='count', names='status',
                title="진행 상태 비율",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig2, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        if 'urgency' in filtered_df.columns and not filtered_df.empty:
            urgency_counts = filtered_df['urgency'].value_counts().reset_index()
            urgency_counts.columns = ['urgency', 'count']
            fig3 = px.bar(
                urgency_counts, x='urgency', y='count',
                title="긴급도별 분포",
                color='urgency',
                color_discrete_map={'상': '#FF4B4B', '보통': '#FFAA00', '하': '#29B6F6'},
                text='count'
            )
            fig3.update_layout(showlegend=False, xaxis_title="긴급도", yaxis_title="건수")
            st.plotly_chart(fig3, use_container_width=True)

    with row2_col2:
        if 'ai_handling' in filtered_df.columns and not filtered_df.empty:
            ai_counts = filtered_df['ai_handling'].value_counts().reset_index()
            ai_counts.columns = ['ai_handling', 'count']
            fig4 = px.pie(
                ai_counts, values='count', names='ai_handling',
                title="AI 활용구분 비율",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig4, use_container_width=True)

    # 6. 날짜별 요청 추이 차트
    if 'request_date' in filtered_df.columns and not filtered_df.empty:
        st.markdown("### 📅 일별 업무 지원 요청 접수 추이")
        date_counts = filtered_df.groupby(filtered_df['request_date'].dt.date).size().reset_index(name='count')
        fig5 = px.line(
            date_counts, x='request_date', y='count',
            title="일자별 접수 건수 추이",
            markers=True
        )
        fig5.update_layout(xaxis_title="접수일자", yaxis_title="건수")
        st.plotly_chart(fig5, use_container_width=True)

    # 7. 상세 데이터 데이터프레임 및 다운로드
    st.markdown("---")
    st.markdown("### 📋 상세 데이터 목록")
    st.dataframe(filtered_df, use_container_width=True)

    # CSV 다운로드 버튼
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 필터링된 데이터 다운로드 (CSV)",
        data=csv_bytes,
        file_name="filtered_work_requests.csv",
        mime="text/csv"
    )

else:
    st.info("👆 상단의 [CSV 파일 업로드] 버튼을 눌러 '업무지원요청_합성자료.csv' 파일이나 동일 형식의 CSV를 등록해 주세요.")
