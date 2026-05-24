import streamlit as st
import json
from pathlib import Path
from collections import defaultdict
import base64

# ----------------- 1. 페이지 설정 -----------------
st.set_page_config(page_title="신선여자고등학교 고교학점제 이수 가이드", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"

# ----------------- 2. 배경 이미지 및 CSS -----------------
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()

def inject_styles():
    img_path = ASSETS_DIR / "school_image.png"
    bg_css = ""
    if img_path.exists():
        img_b64 = get_base64_of_bin_file(str(img_path))
        bg_css = f'''
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url("data:image/png;base64,{img_b64}");
            background-size: cover; background-attachment: fixed;
        }}
        '''
    st.markdown(f"""
    <style>
    {bg_css}
    /* 가독성을 위한 스타일 */
    .subject-card { background: #ffffff !important; border: 2px solid #6366f1 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .subject-card label { font-weight: 900 !important; font-size: 17px !important; color: #000 !important; }
    h1, h2, h3, h4, p, div { color: #000 !important; font-weight: 800 !important; }
    .stCheckbox label { font-weight: 800 !important; font-size: 16px !important; color: #000 !important; }
    .stSelectbox label { font-weight: 900 !important; font-size: 17px !important; color: #000 !important; }
    .stButton > button[kind="primary"] { font-size: 28px !important; font-weight: 900 !important; height: 80px !important; border-radius: 12px !important; background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

inject_styles()

# ----------------- 3. 데이터 로더 -----------------
def load_curriculum(year): return json.load(open(DATA_DIR / f"curriculum_{year}.json", "r", encoding="utf-8"))
def load_career(): return json.load(open(DATA_DIR / "career_recommendations.json", "r", encoding="utf-8")) if (DATA_DIR / "career_recommendations.json").exists() else {}
def load_teacher_comments(): return json.load(open(DATA_DIR / "teacher_comments.json", "r", encoding="utf-8")) if (DATA_DIR / "teacher_comments.json").exists() else {}

if "entry_year" not in st.session_state: st.session_state.entry_year = 2025
if "year_selected" not in st.session_state: st.session_state.year_selected = False
if "selected_subjects" not in st.session_state: st.session_state.selected_subjects = {}

# ----------------- 4. 공통 함수 -----------------
def render_footer():
    st.markdown("<div style='text-align:center; padding:50px 0; border-top:3px solid #000; margin-top:50px;'><p style='font-size:22px; font-weight:900;'>만든 이: 신선여자고등학교 교육과정부 & 교무부</p><p style='font-size:20px; font-weight:900;'>🗓️ 2026.05</p></div>", unsafe_allow_html=True)

# ----------------- 5. 페이지 라우팅 -----------------
with st.sidebar:
    if st.session_state.year_selected:
        year = st.radio("입학년도", [2025, 2026], index=0 if st.session_state.entry_year == 2025 else 1)
        st.session_state.entry_year = year
        page = st.radio("메뉴", ["🏠 홈", "🗺️ 핵심 이수 경로", "📚 학년별 교과목 탐색", "📅 시간표 시뮬레이터", "🎓 2028 대입 권장 과목", "🖨️ 결과 출력"])
    else: page = None

if not st.session_state.year_selected:
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    c_l, c_r = st.columns([1, 1], gap="large")
    with c_l:
        if (ASSETS_DIR / "logo.png").exists(): st.image(str(ASSETS_DIR / "logo.png"), width=150)
        st.markdown("<h1 style='font-size: 50px;'>신선여자고등학교</h1><h2 style='font-size: 40px;'>고교학점제 이수 가이드</h2>", unsafe_allow_html=True)
    with c_r:
        st.markdown("<p style='font-size: 26px; font-weight: 900; margin-bottom: 20px;'>● 입학년도를 선택하세요.</p>", unsafe_allow_html=True)
        if st.button("2025학년도 입학생(2학년) 선택", type="primary"): st.session_state.entry_year=2025; st.session_state.year_selected=True; st.rerun()
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("2026학년도 입학생(1학년) 선택", type="primary"): st.session_state.entry_year=2026; st.session_state.year_selected=True; st.rerun()
else:
    cur = load_curriculum(st.session_state.entry_year)
    if page == "🏠 홈":
        st.header("🏠 홈")
        render_footer()
    elif page == "🗺️ 핵심 이수 경로":
        st.header("🗺️ 핵심 이수 경로")
        render_footer()
    elif page == "📚 학년별 교과목 탐색":
        st.header("📚 학년별 개설 교과목 탐색")
        render_footer()
    elif page == "📅 시간표 시뮬레이터":
        st.header("📅 시간표 시뮬레이터")
        selected = st.session_state.selected_subjects.get(str(st.session_state.entry_year), set())
        for g in cur["groups"]:
            if st.session_state.entry_year == 2025 and any(gid in g["id"] for gid in ["G01", "G02", "G03"]): continue
            st.subheader(f"🔵 {g['id']} 선택")
            subs = [s for s in cur["subjects"] if s["id"] in g["subject_ids"]]
            for pinfo in g["pick_per_sem"]:
                if pinfo["pick"] == 1:
                    options = ["(선택 안 함)"] + [s["name"] for s in subs]
                    choice = st.selectbox(f"{pinfo['sem']} 선택", options, key=f"sel_{g['id']}")
                    for s in subs:
                        if s["name"] == choice: selected.add(s["id"])
                        elif s["name"] != choice and s["id"] in selected: selected.discard(s["id"])
                else:
                    cols = st.columns(3)
                    for i, s in enumerate(subs):
                        if cols[i%3].checkbox(f"{s['name']} ({s.get('op_credit')}학점)", value=(s["id"] in selected), key=f"chk_{s['id']}"): selected.add(s["id"])
                        else: selected.discard(s["id"])
        st.session_state.selected_subjects[str(st.session_state.entry_year)] = selected
        render_footer()
    elif page == "🎓 2028 대입 권장 과목":
        st.header("🎓 2028 대입 전공 연계 권장 교과")
        render_footer()
    elif page == "🖨️ 결과 출력":
        st.header("🖨️ 최종 결과 내역 및 보관")
        final = st.session_state.selected_subjects.get(str(st.session_state.entry_year), set())
        subs = [s for s in cur["subjects"] if s["id"] in final]
        for s in subs: st.markdown(f"<div class='subject-card'>{s['name']} ({s.get('op_credit')}학점)</div>", unsafe_allow_html=True)
        render_footer()
