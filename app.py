import streamlit as st
import json, os
from pathlib import Path
from collections import defaultdict
import base64

# ----------------- 페이지 기본 설정 -----------------
st.set_page_config(
    page_title="신선여자고등학교 고교학점제 이수 가이드북",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"

# ----------------- 배경 이미지 CSS 주입 함수 -----------------
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def inject_global_background():
    school_img_path = ASSETS_DIR / "school_image.png"
    if school_img_path.exists():
        img_base64 = get_base64_of_bin_file(str(school_img_path))
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(248, 250, 255, 0.88), rgba(248, 250, 255, 0.88)), url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

inject_global_background()

# ----------------- 공용 데이터 로더 -----------------
def load_curriculum(year: int):
    path = DATA_DIR / f"curriculum_{year}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_career():
    path = DATA_DIR / "career_recommendations.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_teacher_comments():
    path = DATA_DIR / "teacher_comments.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ----------------- 전역 CSS 스타일 -----------------
st.markdown("""
<style>
/* 💡 [수정] 버튼 폰트 사이즈와 두께 대폭 강화 */
.stButton > button[kind="primary"] {
    font-size: 28px !important;
    font-weight: 900 !important;
    height: 80px !important;
    border-radius: 12px !important;
    letter-spacing: -0.5px !important;
    color: white !important;
    background-color: #ff4b4b !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #ff2b2b !important;
}

.big-card { background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%); border: 1px solid #e0e7ff; border-radius: 16px; padding: 24px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.subject-card { background: rgba(255, 255, 255, 0.9); border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; }
.badge { display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; margin-right: 4px; }
.badge-area { background: #f3f4f6; color: #374151; }
.badge-type-공통 { background: #dbeafe; color: #1e40af; }
.title-gradient { background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.landing-title-pink { color: #f4a8b8; font-size: 52px; font-weight: 900; margin: 0; letter-spacing: -1px; }
.landing-title-black { color: #1f2937; font-size: 44px; font-weight: 900; margin: 5px 0 0 0; letter-spacing: -1px; }
</style>
""", unsafe_allow_html=True)

# ----------------- 세션 상태 초기화 -----------------
if "entry_year" not in st.session_state: st.session_state.entry_year = 2025
if "year_selected" not in st.session_state: st.session_state.year_selected = False
if "selected_subjects" not in st.session_state: st.session_state.selected_subjects = {}

# ----------------- 하단 푸터 함수 -----------------
def render_made_by():
    st.markdown("""
        <div style='text-align: center; padding: 24px 0 16px 0; border-top: 2px solid #e5e7eb; margin-top: 60px;'>
            <p style='font-size: 20px; margin: 0; color: #374151; font-weight: 900;'>
                만든 이: 신선여자고등학교 교육과정부 & 교무부
            </p>
            <p style='font-size: 18px; margin: 6px 0 0 0; color: #4b5563; font-weight: 800;'>
                🗓️ 2026.05
            </p>
        </div>
    """, unsafe_allow_html=True)

# ----------------- 사이드바 설정 -----------------
with st.sidebar:
    st.markdown("<p style='font-size: 20px; color: #555555; font-weight: bold;'>⭐주체적인 삶의 주인공으로 거듭나는 신선여고인을 응원합니다.</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.get("year_selected", False):
        year = st.radio("입학년도 선택", [2025, 2026], format_func=lambda y: f"{y}학년도 ({'2학년' if y==2025 else '1학년'})", index=0 if st.session_state.entry_year != 2026 else 1)
        st.session_state.entry_year = year
        st.markdown("---")
        page = st.radio("메뉴", ["🏠 홈", "🗺️ 핵심 이수 경로", "📚 학년별 교과목 탐색", "📅 시간표 시뮬레이터", "🎓 2028 대입 권장 과목", "🖨️ 결과 출력"])
    else:
        st.info("👉 입학년도를 먼저 선택하세요.")
        page = None
        year = st.session_state.get("entry_year", 2025)

# (이후 함수 및 로직은 기존과 동일)
# ... [이하 기존 코드 그대로 유지] ...

curriculum = load_curriculum(year)
career = load_career()
comments = load_teacher_comments()
SEM_LABELS = {"1-1":"1학년 1학기", "1-2":"1학년 2학기", "2-1":"2학년 1학기", "2-2":"2학년 2학기", "3-1":"3학년 1학기", "3-2":"3학년 2학기", "3-annual": "3학년 (연간)"}

# ---------------- 페이지: 랜딩 (수평 정렬 및 버튼 강화) ----------------
def page_landing():
    # 수직 중앙 배치를 위한 여백
    st.markdown("<div style='height: 22vh;'></div>", unsafe_allow_html=True)
    
    # 💡 1:1 비율의 컬럼으로 좌우 높이를 평행하게 배치
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        # 왼쪽 정렬을 위해 서브 컬럼 사용 (로고와 텍스트를 한 묶음으로)
        sub_l, sub_r = st.columns([1, 3])
        with sub_l:
            logo_path = ASSETS_DIR / "logo.png"
            if logo_path.exists(): st.image(str(logo_path), width=150)
        with sub_r:
            st.markdown("""
            <div style='padding-top: 10px;'>
                <h1 class='landing-title-pink'>신선여자고등학교</h1>
                <h2 class='landing-title-black'>고교학점제 이수 가이드</h2>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        # 오른쪽: 문구와 버튼을 왼쪽 텍스트 높이와 맞춤
        st.markdown("<p style='color: #1f2937; font-size: 26px; font-weight: 900; margin-bottom: 25px;'>● 입학년도를 선택하세요.</p>", unsafe_allow_html=True)
        
        if st.button("2025학년도 입학생 선택 (현재 2학년)", use_container_width=True, type="primary"):
            st.session_state.entry_year = 2025
            st.session_state.year_selected = True
            st.rerun()
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("2026학년도 입학생 선택 (현재 1학년)", use_container_width=True, type="primary"):
            st.session_state.entry_year = 2026
            st.session_state.year_selected = True
            st.rerun()
    
    # 푸터 위치 조정
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    render_made_by()

# ----------------- 페이지: 홈 -----------------
def page_home():
    col_l, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄 학년도 변경", use_container_width=True):
            st.session_state.year_selected = False
            st.rerun()
    st.markdown(f"<h1><span class='title-gradient'>{year}학년도 입학생</span><br>고교학점제 이수 가이드북</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='big-card'><h2>192</h2><p>졸업 필수 학점</p><span class='sub'>교과 174 + 창체 18</span></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='big-card'><h2>122</h2><p>학교지정 학점</p><span class='sub'>필수 이수</span></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='big-card'><h2>52</h2><p>학생선택 학점</p><span class='sub'>택 18과목</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📖 이 가이드북 사용법")
    st.markdown("1. **🗺️ 핵심 이수 경로** — 필수 영역 확인\n2. **📚 학년별 교과목 탐색** — 학기별 과목 카드 확인\n3. **📅 시간표 시뮬레이터** — 직접 선택 및 졸업 요건 자가 진단\n4. **🎓 2028 대입 권장 과목** — 계열별 과목 안내\n5. **🖨️ 결과 출력** — 시뮬레이션 결과 저장")
    render_made_by()

# ----------------- 페이지: 핵심 이수 경로 -----------------
def page_core_path():
    st.markdown("## 🗺️ 핵심 이수 경로")
    areas = curriculum["area_requirements"]
    groups_display = [
        ("📘 기초 교과 (국·수·영)", ["국어","수학","영어"], "학교지정 과목에서 자동 충족"),
        ("🔬 탐구 교과 (사회·과학)", ["사회","과학"], "공통 과목 이수 시 자동 충족"),
        ("👟 체육 교과", ["체육"], "학년별 필수 이수 필수"),
        ("🎨 예술 교과", ["예술"], "음악·미술 학기 교차 이수"),
        ("📐 기술·가정/교양/제2외국어", ["기술.가정/정보","교양","제2외국어/한문"], "공통 필수 16학점 (합산)"),
    ]
    cols = st.columns(3)
    for i, (title, area_list, desc) in enumerate(groups_display):
        with cols[i % 3]:
            req, total = 0, 0
            for a in area_list:
                if a in areas:
                    req += areas[a].get("required", 0)
                    total += areas[a].get("total", 0)
            if "공동 합계" in str([areas[a].get("note","") for a in area_list if a in areas]):
                total = areas[area_list[0]].get("total", 0)
                req = areas[area_list[0]].get("required", 0)
            st.markdown(f"<div class='subject-card' style='min-height:140px'><div style='font-weight:700; font-size:16px; margin-bottom:6px'>{title}</div><div style='color:#4f46e5; font-weight:600'>필수 {req if req > 0 else '-'}학점 · 총 {total}학점</div><div style='color:#6b7280; font-size:13px; margin-top:8px'>{desc}</div></div>", unsafe_allow_html=True)
    render_made_by()

# ----------------- 페이지: 학년별 교과목 탐색 -----------------
def page_explore():
    st.markdown("## 📚 학년별 교과목 탐색")
    tab1, tab2, tab3 = st.tabs(["1학년", "2학년", "3학년"])
    for tab, grade in [(tab1,1),(tab2,2),(tab3,3)]:
        with tab:
            sem_cols = st.columns(2)
            for idx, sem_num in enumerate([1,2]):
                sem_key = f"{grade}-{sem_num}"
                with sem_cols[idx]:
                    st.markdown(f"#### 📅 {grade}학년 {sem_num}학기")
                    show_semester_subjects(sem_key)
    render_made_by()

def show_semester_subjects(sem_key):
    subs = []
    for s in curriculum["subjects"]:
        added = False
        for sem in s.get("semesters", []):
            if sem["sem"] == sem_key or (sem["sem"] == "3-annual" and sem_key.startswith("3-")):
                subs.append((s, sem["credit"])); added = True; break
        if not added:
            for n in s.get("notes", []):
                if n["sem"] == sem_key or (n["sem"] == "3-annual" and sem_key.startswith("3-")):
                    subs.append((s, s.get("op_credit") or 0)); break
    for s, c in [(x,y) for x,y in subs if x["section"]=="학교지정"]: render_subject_card(s, c)
    for s, c in [(x,y) for x,y in subs if x["section"]=="학생선택"]: render_subject_card(s, c)

def render_subject_card(s, sem_credit=None):
    credit = sem_credit if sem_credit else s.get("op_credit") or 0
    yrk = str(curriculum["entry_year"])
    tc = comments.get(yrk, {}).get(s["name"], None)
    tc_html = f"<div style='margin-top:6px; padding:8px; background:#f9fafb; border-radius:6px; font-size:12px; color:#4b5563'>💬 {tc['comment']}</div>" if tc and tc.get("comment") else ""
    st.markdown(f"<div class='subject-card'><div style='display:flex; justify-content:space-between; align-items:center'><div><span class='badge badge-area'>{s['area']}</span><span class='badge badge-type-공통'>{s.get('type','')}</span></div><div style='color:#4f46e5; font-weight:700'>{credit}학점</div></div><div style='font-size:16px; font-weight:600; margin-top:8px'>{s['name']}</div>{tc_html}</div>", unsafe_allow_html=True)

# ----------------- 페이지: 시뮬레이터 -----------------
def page_simulator():
    st.markdown("## 📅 시간표 시뮬레이터")
    yr_key = str(year)
    if yr_key not in st.session_state.selected_subjects: st.session_state.selected_subjects[yr_key] = set()
    selected = st.session_state.selected_subjects[yr_key]
    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}

    for g in curriculum["groups"]:
        if st.session_state.entry_year == 2025 and any(gid in g["id"] for gid in ["G01", "G02", "G03"]): continue
        render_group_picker(g, selected)
            
    final = selected | auto
    st.markdown("---")
    show_summary(final, auto, selected)
    render_made_by()

def render_group_picker(g, selected):
    subs = [s for s in curriculum["subjects"] if s["id"] in g["subject_ids"]]
    pick_total = sum(p["pick"] for p in g["pick_per_sem"])
    st.markdown(f"**[{g['id']}] 선택** (총 {pick_total}과목)")
    for pinfo in g["pick_per_sem"]:
        sem = pinfo["sem"]
        label = "3학년 제2외국어 선택" if sem == "3-annual" else SEM_LABELS.get(sem, sem)
        options = ["(선택 안 함)"] + [s["name"] for s in subs]
        key = f"groupsel_{g['id']}_{sem}"
        choice = st.selectbox(f"  {label}", options, key=key)
        if choice != "(선택 안 함)":
            for s in subs:
                if s["name"] == choice: selected.add(s["id"])
                else: selected.discard(s["id"])

def show_summary(final_ids, auto_ids, picked_ids):
    total_credit = 0
    by_area = {}
    for sid in final_ids:
        s = next((x for x in curriculum["subjects"] if x["id"]==sid), None)
        if not s: continue
        for sem in s.get("semesters", []):
            if sem["sem"] in ["1-1", "1-2"]: # 1학년 학점만 필터링 예시
                total_credit += sem["credit"]
                by_area[s["area"]] = by_area.get(s["area"],0) + sem["credit"]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("총 이수학점", f"{total_credit + 18}")
    c2.metric("졸업요건", "192학점")
    c3.metric("상태", "진행 중")
    st.dataframe([{"교과(군)": a, "이수학점": v} for a, v in by_area.items()], use_container_width=True)

# ----------------- 페이지: 2028 대입 권장 -----------------
def page_career():
    st.markdown("## 🎓 2028 대입 권장 과목")
    if career:
        track = st.selectbox("진로 계열 선택", list(career.keys()))
        st.write(career[track]["summary"])
    render_made_by()

# ----------------- 페이지: 결과 출력 -----------------
def page_print():
    st.markdown("## 🖨️ 결과 출력")
    if st.button("📄 보고서 생성", type="primary"):
        st.success("보고서가 준비되었습니다. (인쇄 메뉴를 이용하세요)")
    render_made_by()

# ---------------- 라우팅 ----------------
if not st.session_state.get("year_selected", False):
    page_landing()
else:
    PAGES = {"🏠 홈": page_home, "🗺️ 핵심 이수 경로": page_core_path, "📚 학년별 교과목 탐색": page_explore, "📅 시간표 시뮬레이터": page_simulator, "🎓 2028 대입 권장 과목": page_career, "🖨️ 결과 출력": page_print}
    PAGES[page]()
