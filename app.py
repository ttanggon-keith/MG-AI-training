import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정 (넓은 레이아웃)
st.set_page_config(page_title="팀 예산 관리", layout="wide")

# HTML 파일 읽기 (동일한 폴더에 team_budget_dashboard.html이 있어야 합니다)
try:
    with open("team_budget_dashboard.html", "r", encoding="utf-8") as f:
        html_code = f.read()
        
    # HTML 컴포넌트를 이용해 브라우저에 출력 (height를 넉넉하게 주어 스크롤 지원)
    components.html(html_code, height=900, scrolling=True)

except FileNotFoundError:
    st.error("HTML 파일을 찾을 수 없습니다. 동일한 경로에 'team_budget_dashboard.html' 파일이 있는지 확인해주세요.")
