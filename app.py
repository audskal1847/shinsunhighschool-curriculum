import streamlit as st
import json
from pathlib import Path
from collections import defaultdict
import base64

# ----------------- 1. 페이지 설정 -----------------
st.set_page_config(page_title="신선여자고등학교 고교학점제 가이드", layout="wide")

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
    .subject-card { background: #ffffff !important; border: 2px solid #6366f1 !important; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .subject-card label { font-weight: 800 !important; font-size: 16px !important; color: #000 !important; }
    h1, h2, h3, h4, p, div { color: #000 !important; font-weight: 800 !important; }
    .stCheckbox label { font-weight: 800 !important; font-size: 16px !important; color: #000 !important; }
    .stSelectbox label { font-weight: 800 !important; font-size: 16px !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

inject_styles()

# ----------------- 3. 데이터 로드 -----------------
def load_curriculum(year): return json.load(open(DATA_DIR / f"curriculum_{year}.json", "r", encoding="utf-8"))

if "entry_year" not in st.session_state: st.session_state.entry_year = 2025
if "year_selected" not in st.session_state: st.session_state.year_selected = False
if "selected_subjects" not in st.session_state: st.session_state.selected_subjects = {}

# ----------------- 4. 페이지 구성 -----------------
def render_footer():
    st.markdown("<div style='text-align:center; padding:50px 0; border-top:2px solid #999; margin-top:50px;'><p style='font-size:20px; font-weight:900;'>만든 이: 신선여자고등학교 교육과정부 & 교무부</p><p style='font-size:18px; font-weight:800;'>🗓️ 2026.05</p></div>", unsafe_allow_html=True)

with st.sidebar:
    if st.session_state.year_selected:
        year = st.radio("입학년도", [2025, 2026], index=0 if st.session_state.entry_year == 2025 else 1)
        st.session_state.entry_year = year
        page = st.radio("메뉴", ["📅 시간표 시뮬레이터", "🖨️ 결과 출력"])
    else: page = None

if not st.session_state.year_selected:
    st.title("신선여자고등학교 고교학점제 가이드")
    if st.button("2025학년도 입학생(2학년) 시작", type="primary"): st.session_state.entry_year=2025; st.session_state.year_selected=True; st.rerun()
    if st.button("2026학년도 입학생(1학년) 시작", type="primary"): st.session_state.entry_year=2026; st.session_state.year_selected=True; st.rerun()
else:
    cur = load_curriculum(st.session_state.entry_year)
    if page == "📅 시간표 시뮬레이터":
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

    elif page == "🖨️ 결과 출력":
        st.header("🖨️ 최종 결과 내역 및 보관")
        final = st.session_state.selected_subjects.get(str(st.session_state.entry_year), set())
        subs = [s for s in cur["subjects"] if s["id"] in final]
        st.subheader("선택한 과목 목록")
        for s in subs: st.markdown(f"<div class='subject-card'>{s['name']} ({s.get('op_credit')}학점) - {s['area']}</div>", unsafe_allow_html=True)
        
        # 워드 다운로드 로직
        html_content = "<html><body><h1>이수 계획서</h1><ul>" + "".join([f"<li>{s['name']}</li>" for s in subs]) + "</ul></body></html>"
        st.download_button("📥 Word 문서로 저장", html_content, "이수계획.doc", "application/msword")
        render_footer()
