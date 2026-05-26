import streamlit as st
import json, os
from pathlib import Path
from collections import defaultdict
import base64

# ----------------- 1. 페이지 기본 설정 -----------------
st.set_page_config(
    page_title="신선여자고등학교 고교학점제 이수 가이드북",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"

# ----------------- 2. 배경 이미지 처리 및 CSS 주입 -----------------
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def inject_styles():
    img_path = ASSETS_DIR / "school_image.png"
    bg_css = ""
    
    # [안전장치] 폴더나 사진 파일이 없어도 에러가 나지 않도록 예외 처리
    try:
        if img_path.exists():
            img_b64 = get_base64_of_bin_file(str(img_path))
            bg_css = f'''
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url("data:image/png;base64,{img_b64}");
                background-size: cover; background-attachment: fixed;
            }}
            '''
    except Exception:
        pass

    st.markdown(f"""
    <style>
    {bg_css}
    /* 카드 디자인 */
    .subject-card, div[data-testid="stVerticalBlockBorderWrapper"] {{ 
        background: #ffffff !important; 
        border: 2px solid #6366f1 !important; 
        border-radius: 12px !important; 
        padding: 20px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; 
        margin-bottom: 10px !important;
    }}
    /* 기본 텍스트 검은색 강제 (가독성 목적) */
    .subject-card label {{ font-weight: 900 !important; font-size: 17px !important; color: #000 !important; }}
    h1, h2, h3, h4, p, div {{ color: #000 !important; font-weight: 800 !important; }}
    
    /* 🔴 [원인 차단] 진로 안내 문구 전용 클래스 - 검은색 강제 규칙을 완벽하게 이겨냅니다 */
    .main-red-notice, .main-red-notice *, div.main-red-notice, p.main-red-notice, span.main-red-notice {{
        color: #ff0000 !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        display: block !important;
    }}
    
    /* 체크박스 레이블 자체를 과목명으로 쓰기 때문에 가독성을 극대화합니다 */
    .stCheckbox label, .stCheckbox label p {{ font-weight: 900 !important; font-size: 19px !important; color: #000000 !important; }}
    .stSelectbox label {{ font-weight: 900 !important; font-size: 17px !important; color: #000 !important; }}
    
    /* 버튼 디자인 및 글자색을 흰색(#ffffff)으로 강제 고정 */
    .stButton > button {{
        font-size: 24px !important; 
        font-weight: 900 !important; 
        height: 80px !important; 
        border-radius: 12px !important; 
        color: #ffffff !important; 
        border: none !important;
    }}
    .stButton > button p {{
        color: #ffffff !important; 
        font-weight: 900 !important;
    }}
    
    /* 기본 버튼 색상 (2025학년도 기본값: 빨간색) */
    .stButton > button[kind="primary"] {{
        background-color: #ff4b4b !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #ff2b2b !important;
    }}

    /* 2026학년도 글씨가 포함된 버튼만 콕 집어서 파란색으로 변경 */
    div.stButton:has(button p:contains("2026학년도")) > button,
    div.stButton:has(button:contains("2026학년도")) > button {{
        background-color: #1e40af !important;
    }}
    div.stButton:has(button p:contains("2026학년도")) > button:hover,
    div.stButton:has(button:contains("2026학년도")) > button:hover {{
        background-color: #1d4ed8 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_styles()

# ----------------- 3. 공용 데이터 로더 -----------------
def load_curriculum(year: int):
    path = DATA_DIR / f"curriculum_{year}.json"
    with open(path, "r", encoding="utf-8") as f: 
        return json.load(f)

@st.cache_data
def load_career():
    path = DATA_DIR / "career_recommendations.json"
    return json.load(open(path, "r", encoding="utf-8")) if path.exists() else {}

@st.cache_data
def load_teacher_comments():
    path = DATA_DIR / "teacher_comments.json"
    return json.load(open(path, "r", encoding="utf-8")) if path.exists() else {}

# ----------------- 4. 글로벌 디자인 및 컴포넌트 CSS -----------------
st.markdown("""
<style>
.big-card { background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%); border: 1px solid #e0e7ff; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; }
.big-card h2 { background: linear-gradient(90deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 56px; margin: 0; font-weight: 800; }
.big-card p { color: #4b5563; margin: 8px 0 0 0; font-weight: 600; }
.big-card .sub { color: #6b7280; font-size: 13px; margin-top: 4px; }
.badge { display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; margin-right: 4px; }
.badge-area { background: #f3f4f6; color: #374151; }
.badge-type-공통 { background: #dbeafe; color: #1e40af; }
.badge-type-일반 { background: #ede9fe; color: #5b21b6; }
.badge-type-진로 { background: #fef3c7; color: #92400e; }
.badge-type-융합 { background: #fce7f3; color: #9d174d; }
.badge-req { background: #dcfce7; color: #166534; }
.badge-sel { background: #fef9c3; color: #854d0e; }
.title-gradient { background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.landing-title-pink { color: #f4a8b8; font-size: 46px; font-weight: 900; margin: 0; }
.landing-title-black { color: #1f2937; font-size: 38px; font-weight: 900; margin: 5px 0 0 0; }
.alert-success { background:#f0fdf4; border-left:4px solid #22c55e; padding:12px; border-radius:8px; color: #166534; }
.alert-warning { background:#fffbeb; border-left:4px solid #f59e0b; padding:12px; border-radius:8px; color: #92400e; }
</style>
""", unsafe_allow_html=True)

# ----------------- 5. 세션 상태 초기화 -----------------
if "entry_year" not in st.session_state: st.session_state.entry_year = 2025
if "year_selected" not in st.session_state: st.session_state.year_selected = False
if "selected_subjects" not in st.session_state: st.session_state.selected_subjects = {}

# ----------------- 6. 하단 고정 공용 푸터 -----------------
def render_made_by():
    st.markdown("""
        <div style='text-align: center; padding: 24px 0; border-top: 2px solid #e5e7eb; margin-top: 60px;'>
            <p style='font-size: 20px; margin: 0; color: #374151; font-weight: 900;'>만든 이: 신선여자고등학교 교육과정부 & 교무부</p>
            <p style='font-size: 18px; margin: 6px 0 0 0; color: #4b5563; font-weight: 800;'>🗓️ 2026.05</p>
        </div>
    """, unsafe_allow_html=True)

# ----------------- 7. 네비게이션 및 사이드바 (PDF 다운로드 추가) -----------------
with st.sidebar:
    st.markdown("<p style='font-size: 20px; color: #555555; font-weight: bold;'>⭐주체적인 삶의 주인공으로 거듭나는 신선여고인을 응원합니다.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.get("year_selected", False):
        year = st.radio("입학년도 선택", [2025, 2026], format_func=lambda y: f"{y}학년도 입학생 ({'현재 2학년' if y==2025 else '현재 1학년'})", index=0 if st.session_state.entry_year != 2026 else 1)
        st.session_state.entry_year = year
        st.markdown("---")
        page = st.radio("메뉴", ["🏠 홈", "🗺️ 핵심 이수 경로", "📚 학년별 교과목 탐색", "📅 시간표 시뮬레이터", "🎓 2028 대입 권장 과목", "🖨️ 결과 출력"])
    else:
        st.info("👉 입학년도를 먼저 선택하세요.")
        page = None
        year = st.session_state.get("entry_year", 2025)

    # 사이드바 하단 PDF 안내서 다운로드 버튼
    st.markdown("---")
    st.markdown("### 📥 자료 다운로드")
    pdf_path = ASSETS_DIR / "2026.subjectguidebook.pdf"
    if pdf_path.exists():
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 선택과목 안내서 다운로드",
                data=pdf_file,
                file_name="2026_선택과목_안내서.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.caption("※ 'assets' 폴더에 '2026.subjectguidebook.pdf' 파일을 넣으면 다운로드 버튼이 활성화됩니다.")

curriculum = load_curriculum(year)
career = load_career()
comments = load_teacher_comments()
SEM_LABELS = {"1-1":"1학년 1학기", "1-2":"1학년 2학기", "2-1":"2학년 1학기", "2-2":"2학년 2학기", "3-1":"3학년 1학기", "3-2":"3학년 2학기", "3-annual": "3학년 (연간)"}

# ----------------- 8. 페이지: 랜딩 -----------------
def page_landing():
    st.markdown("""
    <style>
    .stButton > button[kind="secondary"] {
        background-color: #1e40af !important;
        color: #ffffff !important; 
        font-size: 24px !important;
        font-weight: 900 !important;
        height: 80px !important;
        border-radius: 12px !important;
        border: none !important;
    }
    .stButton > button[kind="secondary"] p {
        color: #ffffff !important;
        font-weight: 900 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #1d4ed8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    c_l, c_r = st.columns([1, 1], gap="large")
    with c_l:
        sub_l, sub_r = st.columns([1, 4])
        with sub_l:
            if (ASSETS_DIR / "logo.png").exists(): st.image(str(ASSETS_DIR / "logo.png"), width=130)
        with sub_r:
            st.markdown("<h1 class='landing-title-pink'>신선여자고등학교</h1><h2 class='landing-title-black'>고교학점제 이수 가이드</h2>", unsafe_allow_html=True)
    with c_r:
        st.markdown("<p style='color: #1f2937; font-size: 24px; font-weight: 900; margin-bottom: 20px;'>● 입학년도를 선택하세요.</p>", unsafe_allow_html=True)
        if st.button("2025학년도 입학생 선택 (현재 2학년)", use_container_width=True, type="primary"):
            st.session_state.entry_year = 2025; st.session_state.year_selected = True; st.rerun()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("2026학년도 입학생 선택 (현재 1학년)", use_container_width=True, type="secondary"):
            st.session_state.entry_year = 2026; st.session_state.year_selected = True; st.rerun()
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    render_made_by()

# ----------------- 9. 페이지: 홈 -----------------
def page_home():
    col_l, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄 학년도 변경", use_container_width=True):
            st.session_state.year_selected = False; st.rerun()

    st.markdown(f"<h1><span class='title-gradient'>{year}학년도 입학생</span><br>고교학점제 이수 가이드북</h1>", unsafe_allow_html=True)
    st.caption("성공적인 고교학점제 마무리를 위한 진로 학업 설계 가이드북")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='big-card'><h2>192</h2><p>졸업 필수 학점</p><span class='sub'>교과 174 + 창체 18</span></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='big-card'><h2>122</h2><p>학교지정 학점</p><span class='sub'>필수 이수 공통과목</span></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='big-card'><h2>52</h2><p>학생선택 학점</p><span class='sub'>최소 택 18과목 이상</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📖 이 가이드북 사용법")
    st.markdown("1. **🗺️ 핵심 이수 경로** — 졸업까지 반드시 충족해야 하는 영역별 학점 확인\n2. **📚 학년별 교과목 탐색** — 학교에 개설된 모든 과목 상세 정보 파악\n3. **📅 시간표 시뮬레이터** — 모의 선택을 통한 졸업 요건 자가 진단\n4. **🎓 2028 대입 권장 과목** — 본인의 진로 계열과 학과에 최적화된 추천 교과 확인\n5. **🖨️ 결과 출력** — 설계 내용을 확인하고 워드/HTML 파일로 다운로드 보관")
    render_made_by()

# ----------------- 10. 페이지: 핵심 이수 경로 -----------------
def page_core_path():
    st.markdown("## 🗺️ 핵심 이수 경로")
    areas = curriculum["area_requirements"]
    groups_display = [
        ("📘 기초 교과 (국·수·영)", ["국어","수학","영어"], "지정 교과만 정상 이수하면 기준 자동 도달"),
        ("🔬 탐구 교과 (사회·과학)", ["사회","과학"], "융합과 선택 지정을 고르게 이수하여 충족"),
        ("👟 체육 교과", ["체육"], "3개 학년 내내 단절 없이 연속 수강 필요"),
        ("🎨 예술 교과", ["예술"], "음악과 미술 간 학기별 상호 교차 집중 수강"),
        ("📐 기술·가정/정보/외국어/교양", ["기술.가정/정보","교양","제2외국어/한문"], "세부 영역 합산 총 16학점 필수 필수"),
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
            st.markdown(f"<div class='subject-card' style='min-height:140px'><div style='font-weight:700; font-size:16px; margin-bottom:6px'>{title}</div><div style='color:#4f46e5; font-weight:600'>필수 최소 {req if req > 0 else '-'}학점 / 총 운영 {total}학점</div><div style='color:#6b7280; font-size:13px; margin-top:8px'>{desc}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 영역별 상세 학점 구조")
    rows = [{"교과(군)": a, "총 운영학점": info.get("total"), "필수 이수학점": info.get("required"), "비고": info.get("note", "")} for a, info in areas.items()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    render_made_by()

# ----------------- 11. 페이지: 학년별 교과목 탐색 -----------------
def page_explore():
    st.markdown("## 📚 학년별 개설 교과목 탐색")
    tab1, tab2, tab3 = st.tabs(["1학년", "2학년", "3학년"])
    for tab, grade in [(tab1,1),(tab2,2),(tab3,3)]:
        with tab:
            sem_cols = st.columns(2)
            for idx, sem_num in enumerate([1,2]):
                sem_key = f"{grade}-{sem_num}"
                with sem_cols[idx]:
                    st.markdown(f"#### 📅 {grade}학년 {sem_num}학기 개설 과목")
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

    required = [(s,c) for (s,c) in subs if s["section"]=="학교지정"]
    selective = [(s,c) for (s,c) in subs if s["section"]=="학생선택"]

    if required:
        with st.expander(f"✅ 필수 이수 과목 ({len(required)}과목)", expanded=True):
            for s, c in required: render_subject_card(s, c)
    if selective:
        gmap = defaultdict(list)
        for s, c in selective: gmap[s["group_id"]].append((s,c))
        for gid, items in gmap.items():
            g = next((x for x in curriculum["groups"] if x["id"]==gid), None)
            pick_label = f" (택{g['pick_per_sem'][0]['pick']})" if g and g.get("pick_per_sem") else ""
            with st.expander(f"🔵 학생선택 묶음 {gid}{pick_label} · {len(items)}과목 중 선택", expanded=False):
                for s, c in items: render_subject_card(s, c)

def render_subject_card(s, sem_credit=None, simulator_mode=False, selected_set=None, checkbox_key=None):
    credit = sem_credit if sem_credit else s.get("op_credit") or 0
    typ = s.get("type","")
    b_map = {"공통": "badge-type-공통", "일반": "badge-type-일반", "진로": "badge-type-진로", "융합": "badge-type-융합"}
    b_cls = b_map.get(typ, "badge-area")
    req_badge = "<span class='badge badge-req'>필수</span>" if s["section"]=="학교지정" else "<span class='badge badge-sel'>선택</span>"
    yrk = str(curriculum["entry_year"])
    tc = comments.get(yrk, {}).get(s["name"], None)
    tc_html = f"<div style='margin-top:6px; padding:8px; background:#f9fafb; border-radius:6px; font-size:12px; color:#4b5563'>💬 {tc['comment']}</div>" if tc and tc.get("comment") else ""
    
    with st.container(border=True):
        st.markdown(f"""
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;'>
            <div>
                <span class='badge badge-area'>{s['area']}</span>
                <span class='badge {b_cls}'>{typ}</span>
                {req_badge}
            </div>
            <div style='color:#4f46e5; font-weight:700;'>{credit}학점</div>
        </div>
        """, unsafe_allow_html=True)
        
        if simulator_mode and selected_set is not None and checkbox_key is not None:
            val = st.checkbox(s["name"], value=(s["id"] in selected_set), key=checkbox_key)
            if val: selected_set.add(s["id"])
            else: selected_set.discard(s["id"])
        else:
            st.markdown(f"<div style='font-size:18px; font-weight:700; mt:4px; color:#000; mb:8px;'>{s['name']}</div>", unsafe_allow_html=True)
            
        if tc_html:
            st.markdown(tc_html, unsafe_allow_html=True)
            
        if "description" in s:
            with st.expander("📖 과목 가이드 (핵심 아이디어 및 내용 요소)"):
                st.markdown(f"**📌 핵심 아이디어**<br>{s['description']['core_idea']}", unsafe_allow_html=True)
                st.markdown("**📋 단원 핵심 내용 요소**", unsafe_allow_html=True)
                for element in s['description']['content_elements']:
                    st.markdown(f"- {element}")

# ----------------- 12. 페이지: 시간표 시뮬레이터 -----------------
def page_simulator():
    st.markdown("## 📅 시간표 시뮬레이터")
    st.caption("학교지정 과목은 고정 처리됩니다. 학생선택군 카드 내부의 과목 수를 정확히 맞추어 설계해 주세요.")

    yr_key = str(year)
    if yr_key not in st.session_state.selected_subjects: st.session_state.selected_subjects[yr_key] = set()
    selected = st.session_state.selected_subjects[yr_key]

    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}

    st.markdown("### 🔵 학생선택 묶음 (그룹별 선택)")
    for g in curriculum["groups"]:
        if st.session_state.entry_year == 2025 and any(gid in g["id"] for gid in ["G01", "G02", "G03"]):
            continue
        if g["id"].startswith("2025-G") or g["id"].startswith("2026-G"):
            render_group_picker(g, selected)
            
    st.markdown("### 🟣 제2외국어 및 한문 학년 단위 지정군")
    for g in curriculum["groups"]:
        if g["id"].endswith("H01"):
            render_group_picker(g, selected)

    final = selected | auto
    st.markdown("---")
    st.markdown("### 📊 이수 학점 종합 결과")
    show_summary(final, auto, selected)
    render_made_by()

def render_group_picker(g, selected):
    subs = [s for s in curriculum["subjects"] if s["id"] in g["subject_ids"]]
    pick_total = sum(p["pick"] for p in g["pick_per_sem"])
    sem_labels = ", ".join(SEM_LABELS.get(p["sem"], p["sem"]) + f" 택{p['pick']}" for p in g["pick_per_sem"])
    st.markdown(f"**[{g['id']}] {sem_labels}** (연간 총 {g.get('total_credit','-')}학점 이수)")

    for pinfo in g["pick_per_sem"]:
        sem = pinfo["sem"]
        label = "3학년 제2외국어 연간 선택과목" if sem == "3-annual" else SEM_LABELS.get(sem, sem)
        
        if pinfo["pick"] == 1:
            options = ["(선택 안 함)"] + [s["name"] for s in subs]
            key = f"groupsel_{g['id']}_{sem}"
            current_choice = st.session_state.get(key, "(선택 안 함)")
            choice = st.selectbox(f"  {label} (택 1과목)", options, key=key, index=options.index(current_choice) if current_choice in options else 0)
            
            for s in subs: selected.discard(s["id"])
            if choice != "(선택 안 함)":
                for s in subs:
                    if s["name"] == choice: selected.add(s["id"])
                    
        else:
            st.caption(f"※ 하단 목록 중 조건에 맞춰 **정확히 {pinfo['pick']}개 과목**을 체크하세요.")
            n_cols = 3
            rows = (len(subs) + n_cols - 1) // n_cols
            for ri in range(rows):
                cc = st.columns(n_cols)
                for ci in range(n_cols):
                    idx = ri * n_cols + ci
                    if idx >= len(subs): break
                    s = subs[idx]
                    key = f"chk_{g['id']}_{s['id']}"
                    with cc[ci]:
                        render_subject_card(s, simulator_mode=True, selected_set=selected, checkbox_key=key)
            
            in_sel = [s for s in subs if s["id"] in selected]
            if len(in_sel) == pinfo["pick"]: st.success(f"✅ 조건 충족 완료 ({len(in_sel)}/{pinfo['pick']})")
            elif len(in_sel) > pinfo["pick"]: st.error(f"❌ 선택 과목 초과 (기준 대비 {len(in_sel)-pinfo['pick']}개 해제 필요)")
            elif len(in_sel) > 0: st.warning(f"⚠️ 추가 선택 필요 ({pinfo['pick']-len(in_sel)}개 과목 더 선택)")

def show_summary(final_ids, auto_ids, picked_ids):
    total_credit = 0
    by_area = {}
    by_sem = {f"{g}-{s}":0 for g in (1,2,3) for s in (1,2)}
    by_type = {"공통":0,"일반":0,"진로":0,"융합":0}

    for sid in final_ids:
        s = next((x for x in curriculum["subjects"] if x["id"]==sid), None)
        if not s: continue
        
        if s.get("semesters"):
            for sem in s["semesters"]:
                c = sem["credit"]
                total_credit += c
                by_area[s["area"]] = by_area.get(s["area"],0) + c
                sem_key = "3-1" if sem["sem"] == "3-annual" else sem["sem"]
                by_sem[sem_key] = by_sem.get(sem_key,0) + c
                by_type[s.get("type","")] = by_type.get(s.get("type",""),0) + c
        else:
            c = s.get("op_credit") or 0
            total_credit += c
            by_area[s["area"]] = by_area.get(s["area"],0) + c
            by_type[s.get("type","")] = by_type.get(s.get("type",""),0) + c

    grand = total_credit + 18

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("총 교과 이수학점", f"{total_credit}", delta="기준 174학점")
    c2.metric("창의적 체험활동", "18학점", delta="고정 이수")
    c3.metric("최종 합계 학점", f"{grand}", delta="졸업 요건 192")
    c4.metric("최종 담은 과목 수", f"{len(final_ids)}개")

    st.markdown("#### 📐 교과군 필수 조건 만족 점검")
    req_data = []
    for a, info in curriculum["area_requirements"].items():
        got = by_area.get(a, 0)
        req = info.get("required") or 0
        status = "✅ 충족" if got >= req else "❌ 미달"
        req_data.append({"교과 영역군": a, "현재설계학점": got, "필수최소학점": req, "달성 비율": f"{(got/req*100) if req else 0:.0f}%", "판정": status, "교과 상세 안내": info.get("note","")})
    st.dataframe(req_data, use_container_width=True, hide_index=True)

    issues = []
    for g in curriculum["groups"]:
        if st.session_state.entry_year == 2025 and any(gid in g["id"] for gid in ["G01", "G02", "G03"]): continue
        picked = sum(1 for sid in g["subject_ids"] if sid in picked_ids)
        target = sum(p["pick"] for p in g["pick_per_sem"])
        if picked != target: issues.append(f"묶음 [{g['id']}]: 지정 기준 {target}과목 중 현재 {picked}과목 선택됨")

    if not issues and total_credit >= 174:
        st.markdown("<div class='alert-success'>🎉 <b>교육과정 설계 요건을 완벽히 달성했습니다!</b> 졸업 및 학점 기준 조건에 모두 합격입니다.</div>", unsafe_allow_html=True)
    else:
        msg = "<div class='alert-warning'><b>⚠️ 다음 보완 조치 사항들을 조정해 주세요:</b><ul>"
        for i in issues: msg += f"<li>{i}</li>"
        if total_credit < 174: msg += f"<li>교과 전체 총이수 전체 학점이 부족합니다. (현재 {total_credit}학점 / 최소 기준 174학점)</li>"
        msg += "</ul></div>"
        st.markdown(msg, unsafe_allow_html=True)

# ----------------- 13. 페이지: 대입 권장 과목 -----------------
def page_career():
    st.markdown("## 🎓 2028 대입 전공 연계 권장 교과 안내")
    if not career: st.info("진로 계열 데이터가 없습니다."); return
    
    # 💡 [핵심 교정] 새롭게 부여된 클래스 이름으로 검은색 고정 장벽을 이기고 강제로 빨간색을 출력시킵니다.
    st.markdown("<div class='main-red-notice'>🔴 본인의 진로 지향 계열을 선택해 주세요.</div>", unsafe_allow_html=True)
    track = st.selectbox("계열 선택", list(career.keys()), label_visibility="collapsed")
    info = career[track]

    st.markdown(f"### 🎯 계열 가이드: {track}")
    st.write(f"**직무 및 전공 설명:** {info.get('summary','')}")
    st.info(f"💡 {info.get('탐구과목_안내','')}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🟢 학과별 필수 권장 교과 목록")
        for n in info.get("필수권장", []):
            offered = any(s["name"]==n or n in s["name"] for s in curriculum["subjects"])
            st.markdown(f"- {'✅' if offered else '⚠️'} **{n}** {'(본교 개설)' if offered else '(개별 보완 필요)'}")
    with c2:
        st.markdown("#### ✨ 학생부 종합 우대 반영 교과 목록")
        for n in info.get("우대", []):
            offered = any(s["name"]==n or n in s["name"] for s in curriculum["subjects"])
            st.markdown(f"- {'✅' if offered else '⚠️'} **{n}** {'(본교 개설)' if offered else '(개별 보완 필요)'}")
    render_made_by()

# ----------------- 14. 페이지: 결과 출력 보고서 -----------------
def page_print():
    st.markdown("## 🖨️ 최종 결과 내역 및 보관")
    st.caption("시뮬레이터에서 선택한 결과가 아래에 실시간으로 표시됩니다. 내용을 확인하고 파일로 다운로드하세요.")

    yr_key = str(year)
    picked = st.session_state.selected_subjects.get(yr_key, set())
    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}
    final = picked | auto

    c1, c2, c3 = st.columns(3)
    with c1: name = st.text_input("학생 성명 (선택사항)", "")
    with c2: sclass = st.text_input("학번 고유 정보 (선택사항)", "")
    with c3: counselor = st.text_input("상담 확인 교사 (선택사항)", "")

    html = build_report_html(name, sclass, counselor, final)
    
    st.markdown("---")
    st.markdown("### 📥 파일 다운로드 및 인쇄")
    
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("📥 MS Word 문서 다운로드 (.doc)", data=html.encode('utf-8-sig'), file_name=f"신선여고_이수계획서_{name or '학생용'}.doc", mime="application/msword", use_container_width=True)
    with d2:
        st.download_button("📥 웹 HTML 원본 다운로드", data=html.encode('utf-8'), file_name=f"신선여고_이수계획서_{name or '학생용'}.html", mime="text/html", use_container_width=True)
    with d3:
        rows = ["영역,교과유형,과목명,운영학점,배정구분"]
        for sid in sorted(final):
            s = next((x for x in curriculum["subjects"] if x["id"]==sid), None)
            if s: rows.append(f'"{s["area"]}","{s.get("type","")}","{s["name"]}",{s.get("op_credit","")},"{s["section"]}"')
        st.download_button("📥 Excel 연동 CSV 다운로드", data="\n".join(rows).encode("utf-8-sig"), file_name=f"신선여고_선택교과목록_{name or '학생용'}.csv", mime="text/csv", use_container_width=True)
        
    st.info("💡 **가장 깔끔한 PDF 보관 팁:** 하단 미리보기 창 영역 내부 혹은 HTML 다운로드 파일을 연 후 브라우저 단축키 **인쇄(Ctrl + P)** 명령을 실행한 뒤, 프린터 대상을 **'PDF로 저장'** 파일 형태로 저장하시면 깨짐 없는 서식 본문 그대로 영구 저장이 가능합니다.")
    
    st.markdown("### 📄 내 선택 결과 미리보기")
    st.components.v1.html(html, height=800, scrolling=True)
    render_made_by()

def build_report_html(name, sclass, counselor, final_ids):
    subs = [s for s in curriculum["subjects"] if s["id"] in final_ids]
    by_sem = defaultdict(list)
    for s in subs:
        if s.get("semesters"):
            for sem in s["semesters"]:
                by_sem["3-1" if sem["sem"] == "3-annual" else sem["sem"]].append((s, sem["credit"]))
        else:
            g = next((x for x in curriculum["groups"] if s["id"] in x["subject_ids"]), None)
            sem_key = g["pick_per_sem"][0]["sem"] if g else "?"
            by_sem["3-1" if sem_key == "3-annual" else sem_key].append((s, s.get("op_credit") or 0))

    rows_html = ""
    grand_total = 0
    for sem in ["1-1","1-2","2-1","2-2","3-1","3-2"]:
        items = by_sem.get(sem, [])
        sem_total = sum(c for _,c in items)
        grand_total += sem_total
        rows_html += f"<tr><td colspan='5' class='sem-hd'>{SEM_LABELS.get(sem, sem)} 배정 (정규교과 {sem_total}학점 + 자율체험 3학점 = 총 {sem_total+3}학점)</td></tr>"
        for s, c in items:
            rows_html += f"<tr><td>{s['area']}</td><td>{s.get('type','')}</td><td>{s['name']}</td><td>{c}학점</td><td>{'공통지정' if s['section']=='학교지정' else '학생진로선택'}</td></tr>"

    return f"""<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head><meta charset='utf-8'>
<style>
body {{ font-family: 'Malgun Gothic', sans-serif; padding: 25px; line-height: 1.5; }}
.info-box {{ background:#f3f4f6; padding:15px; border-radius:6px; margin: 15px 0; border: 1px solid #d1d5db; }}
table {{ width:100%; border-collapse: collapse; margin-top: 15px; }}
th, td {{ border:1px solid #9ca3af; padding:10px; font-size: 13px; text-align: left; }}
th {{ background:#f3f4f6; font-weight: bold; }}
.sem-hd {{ background:#fef3c7; font-weight: bold; color: #b45309; }}
.total {{ font-size: 16px; font-weight: bold; color:#4f46e5; margin-top:20px; }}
</style></head><body>
<h2>🎓 신선여자고등학교 고교학점제 학생 종합 이수계획 확인서</h2>
<div class='info-box'>
<b>대상 교육과정:</b> {year}학년도 입학생 설계 표준 &nbsp;&nbsp;|&nbsp;&nbsp; <b>학생 성명:</b> {name or '미입력'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>학번 소속:</b> {sclass or '미입력'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>상담 지도교사:</b> {counselor or '확인자 공란'}
</div>
<table><thead><tr><th>지정교과 영역군</th><th>과목 대분류</th><th>선택 확정 교과목명</th><th>배정 학점</th><th>이수 형태 구분</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<div class='total'>※ 최종 집계 합산 결과: 교과 총합 {grand_total}학점 + 창의체험형 활동 18학점 = <b>최종 합계 {grand_total + 18}학점</b> (졸업 기준선 192학점 충족 여부 확인용)</div>
</body></html>"""

# ----------------- 15. 메인 마운트 라우팅 제어 -----------------
if not st.session_state.get("year_selected", False):
    page_landing()
else:
    if page == "🏠 홈": page_home()
    elif page == "🗺️ 핵심 이수 경로": page_core_path()
    elif page == "📚 학년별 교과목 탐색": page_explore()
    elif page == "📅 시간표 시뮬레이터": page_simulator()
    elif page == "🎓 2028 대입 권장 과목": page_career()
    elif page == "🖨️ 결과 출력": page_print()
