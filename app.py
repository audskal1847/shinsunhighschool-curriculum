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
        # 💡 [핵심] .stApp 전체 배경으로 지정하고, 반투명한 흰색 그라데이션을 덧씌워 은은하게 만듭니다.
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

# 배경화면 함수 실행 (전체 페이지 적용)
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
.big-card { background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%); border: 1px solid #e0e7ff; border-radius: 16px; padding: 24px; text-align: center; transition: all 0.2s; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.big-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(99,102,241,.15); }
.big-card h2 { background: linear-gradient(90deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 56px; margin: 0; font-weight: 800; }
.big-card p { color: #4b5563; margin: 8px 0 0 0; font-weight: 600; }
.big-card .sub { color: #6b7280; font-size: 13px; margin-top: 4px; }
.subject-card { background: rgba(255, 255, 255, 0.9); border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; transition: all 0.15s; }
.subject-card:hover { border-color: #6366f1; box-shadow: 0 4px 12px rgba(99,102,241,.08); }
.badge { display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; margin-right: 4px; }
.badge-area { background: #f3f4f6; color: #374151; }
.badge-type-공통 { background: #dbeafe; color: #1e40af; }
.badge-type-일반 { background: #ede9fe; color: #5b21b6; }
.badge-type-진로 { background: #fef3c7; color: #92400e; }
.badge-type-융합 { background: #fce7f3; color: #9d174d; }
.badge-req { background: #dcfce7; color: #166534; }
.badge-sel { background: #fef9c3; color: #854d0e; }
.title-gradient { background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
.alert-success { background:#f0fdf4; border-left:4px solid #22c55e; padding:12px; border-radius:8px; }
.alert-warning { background:#fffbeb; border-left:4px solid #f59e0b; padding:12px; border-radius:8px; }
.landing-title-pink { color: #f4a8b8; font-size: 48px; font-weight: 900; margin: 0; letter-spacing: -1px; }
.landing-title-black { color: #1f2937; font-size: 46px; font-weight: 900; margin: 8px 0 0 0; letter-spacing: -1px; }
.stButton > button[kind="primary"] { font-size: 20px !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- 세션 상태 초기화 -----------------
if "entry_year" not in st.session_state: st.session_state.entry_year = 2025
if "year_selected" not in st.session_state: st.session_state.year_selected = False
if "selected_subjects" not in st.session_state: st.session_state.selected_subjects = {}

# ----------------- 하단 푸터 함수 -----------------
def render_made_by():
    st.markdown("""
        <div style='text-align: center; padding: 24px 0 16px 0; border-top: 1px solid #e5e7eb; margin-top: 40px;'>
            <p style='font-size: 16px; margin: 0; color: #4b5563; font-weight: 600;'>
                만든 이: 신선여자고등학교 교육과정부 & 교무부
            </p>
            <p style='font-size: 14px; margin: 4px 0 0 0; color: #6b7280;'>
                🗓️ 2026.05
            </p>
        </div>
    """, unsafe_allow_html=True)

# ----------------- 사이드바 설정 -----------------
with st.sidebar:
    st.markdown("<p style='font-size: 20px; color: #555555; font-weight: bold;'>⭐주체적인 삶의 주인공으로 거듭나는 신선여고인을 응원합니다.</p>", unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.get("year_selected", False):
        year = st.radio(
            "입학년도 선택",
            [2025, 2026],
            format_func=lambda y: f"{y}학년도 입학생 ({'현재 2학년' if y==2025 else '현재 1학년'})",
            index=0 if st.session_state.entry_year != 2026 else 1,
        )
        st.session_state.entry_year = year
        st.markdown("---")
        page = st.radio("메뉴", ["🏠 홈", "🗺️ 핵심 이수 경로", "📚 학년별 교과목 탐색", "📅 시간표 시뮬레이터", "🎓 2028 대입 권장 과목", "🖨️ 결과 출력"])
    else:
        st.info("👉 가장 먼저 입학년도를 선택해야 합니다.")
        page = None
        year = st.session_state.get("entry_year", 2025)

# 데이터 로드
if page is not None or not st.session_state.year_selected:
    curriculum = load_curriculum(year)
    career = load_career()
    comments = load_teacher_comments()

SEM_LABELS = {
    "1-1":"1학년 1학기", "1-2":"1학년 2학기", 
    "2-1":"2학년 1학기", "2-2":"2학년 2학기", 
    "3-1":"3학년 1학기", "3-2":"3학년 2학기", 
    "3-annual": "3학년 (연간)"
}

# ---------------- 페이지: 랜딩 ----------------
def page_landing():
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    
    # 로고 + 학교명 영역
    pad_l, col_logo, col_title, pad_r = st.columns([2, 1.2, 2.8, 1.5], gap="small")
    with col_logo:
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists(): st.image(str(logo_path), width=200)
        else: st.markdown("<div style='text-align:center; font-size:100px;'>🎓</div>", unsafe_allow_html=True)
    with col_title:
        st.markdown("""<div style='padding: 20px 0 0 0;'><h1 class='landing-title-pink'>신선여자고등학교</h1><h2 class='landing-title-black'>고교학점제 이수 가이드</h2></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #1f2937; font-size: 22px; font-weight: 600;'>● 입학년도를 선택하세요.</p>", unsafe_allow_html=True)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("2025학년도 입학생 선택 (현재 2학년)", use_container_width=True, type="primary"):
            st.session_state.entry_year = 2025
            st.session_state.year_selected = True
            st.rerun()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("2026학년도 입학생 선택 (현재 1학년)", use_container_width=True, type="primary"):
            st.session_state.entry_year = 2026
            st.session_state.year_selected = True
            st.rerun()
    
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    render_made_by()

# ----------------- 페이지: 홈 -----------------
def page_home():
    col_l, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄 학년도 변경", use_container_width=True):
            st.session_state.year_selected = False
            st.rerun()

    st.markdown(f"<h1><span class='title-gradient'>{year}학년도 입학생</span><br>고교학점제 이수 가이드북</h1>", unsafe_allow_html=True)
    st.caption("성공적인 고교학점제 마무리를 위한 진로 학업 설계 가이드북")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='big-card'><h2>192</h2><p>졸업 필수 학점</p><span class='sub'>교과 174 + 창체 18</span></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='big-card'><h2>122</h2><p>학교지정 학점</p><span class='sub'>필수 이수</span></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='big-card'><h2>52</h2><p>학생선택 학점</p><span class='sub'>택 18과목</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📖 이 가이드북 사용법")
    st.markdown("1. **🗺️ 핵심 이수 경로** — 졸업까지 반드시 이수해야 하는 영역과 학점을 확인하세요.\n2. **📚 학년별 교과목 탐색** — 학년·학기별 과목 카드를 살펴보세요.\n3. **📅 시간표 시뮬레이터** — 직접 과목을 체크해보고 졸업 요건 충족 여부를 확인하세요.\n4. **🎓 2028 대입 권장 과목** — 진로 계열별 추천 과목을 안내합니다.\n5. **🖨️ 결과 출력** — 시뮬레이션 결과를 워드/HTML/CSV로 저장해 상담 자료로 활용하세요.")
    render_made_by()

# ----------------- 페이지: 핵심 이수 경로 -----------------
def page_core_path():
    st.markdown("## 🗺️ 핵심 이수 경로")
    areas = curriculum["area_requirements"]
    groups_display = [
        ("📘 기초 교과 (국·수·영)", ["국어","수학","영어"], "각 영역 필수 학점을 학교지정 과목에서 자동 충족"),
        ("🔬 탐구 교과 (사회·과학)", ["사회","과학"], "한국사·통합사회·통합과학 이수 시 자동 충족"),
        ("👟 체육 교과", ["체육"], "1~2학년 학기당 2학점, 3학년 학기당 1학점"),
        ("🎨 예술 교과", ["예술"], "음악·미술 학기 교차 이수 / 진로선택 과목"),
        ("📐 기술·가정/정보/제2외국어/교양", ["기술.가정/정보","교양","제2외국어/한문"], "공통 필수 16학점 (세 교과군 합산)"),
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
            req_str = req if req > 0 else "-"
            st.markdown(f"<div class='subject-card' style='min-height:140px'><div style='font-weight:700; font-size:16px; margin-bottom:6px'>{title}</div><div style='color:#4f46e5; font-weight:600'>필수 {req_str}학점 · 총 운영 {total}학점</div><div style='color:#6b7280; font-size:13px; margin-top:8px'>{desc}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 영역별 상세 학점")
    rows = [{"교과(군)": a, "총 운영학점": info.get("total"), "필수 이수학점": info.get("required"), "비고": info.get("note", "")} for a, info in areas.items()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
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
                subs.append((s, sem["credit"]))
                added = True
                break
        if not added:
            for n in s.get("notes", []):
                if n["sem"] == sem_key or (n["sem"] == "3-annual" and sem_key.startswith("3-")):
                    subs.append((s, s.get("op_credit") or 0))
                    break

    required = [(s,c) for (s,c) in subs if s["section"]=="학교지정"]
    selective = [(s,c) for (s,c) in subs if s["section"]=="학생선택"]

    if required:
        with st.expander(f"✅ 필수 이수 과목 ({len(required)}과목)", expanded=True):
            for s, c in required: render_subject_card(s, c)
    if selective:
        gmap = defaultdict(list)
        for s, c in selective: gmap[s["group_id"]].append((s,c))
        for gid, items in gmap.items():
            g = next((g for g in curriculum["groups"] if g["id"]==gid), None)
            pick_label = ""
            if g:
                picks = [p for p in g["pick_per_sem"] if p["sem"]==sem_key or p["sem"]=="3-annual"]
                if picks: pick_label = f" (택{picks[0]['pick']})"
            with st.expander(f"🔵 학생선택 묶음 {gid}{pick_label} · {len(items)}과목 중 선택", expanded=False):
                if g: st.caption(f"이 묶음의 총 이수학점: **{g.get('total_credit')}학점**")
                for s, c in items: render_subject_card(s, c)

def render_subject_card(s, sem_credit=None):
    credit = sem_credit if sem_credit else s.get("op_credit") or 0
    typ = s.get("type","")
    badge_cls = f"badge-type-{typ}" if typ in ("공통","일반","진로","융합") else "badge-area"
    req_badge = "<span class='badge badge-req'>필수</span>" if s["section"]=="학교지정" else "<span class='badge badge-sel'>선택</span>"
    yrk = str(curriculum["entry_year"])
    tc = comments.get(yrk, {}).get(s["name"], None)
    tc_html = f"<div style='margin-top:6px; padding:8px; background:#f9fafb; border-radius:6px; font-size:12px; color:#4b5563'>💬 {tc['comment']}</div>" if tc and tc.get("comment") else ""
    st.markdown(f"<div class='subject-card'><div style='display:flex; justify-content:space-between; align-items:center'><div><span class='badge badge-area'>{s['area']}</span><span class='badge {badge_cls}'>{typ}</span>{req_badge}</div><div style='color:#4f46e5; font-weight:700'>{credit}학점</div></div><div style='font-size:16px; font-weight:600; margin-top:8px'>{s['name']}</div>{tc_html}</div>", unsafe_allow_html=True)

# ----------------- 페이지: 시뮬레이터 -----------------
def page_simulator():
    st.markdown("## 📅 나의 시간표 시뮬레이터")
    st.caption("학교지정 과목은 자동으로 포함됩니다. 학생선택 묶음에서 정해진 개수만큼 선택하세요.")

    yr_key = str(year)
    if yr_key not in st.session_state.selected_subjects: st.session_state.selected_subjects[yr_key] = set()
    selected = st.session_state.selected_subjects[yr_key]

    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}

    st.markdown("### 🔵 학생선택 묶음 (그룹별 택N)")
    for g in curriculum["groups"]:
        # 💡 2학년(2025입학생)은 2학년 그룹(G01, G02, G03)을 화면에서 건너뜀
        if st.session_state.entry_year == 2025:
            if any(gid in g["id"] for gid in ["G01", "G02", "G03"]):
                continue
                
        if g["id"].startswith("2025-G") or g["id"].startswith("2026-G"):
            render_group_picker(g, selected)
            
    st.markdown("### 🟣 학교지정 내 택N 묶음 (제2외국어 등)")
    for g in curriculum["groups"]:
        if g["id"].endswith("H01") or "H" in g["id"].split("-")[1]:
            render_group_picker(g, selected)

    final = selected | auto
    st.markdown("---")
    st.markdown("### 📊 이수 학점 종합")
    show_summary(final, auto, selected)
    render_made_by()

def render_group_picker(g, selected):
    subs = [s for s in curriculum["subjects"] if s["id"] in g["subject_ids"]]
    pick_total = sum(p["pick"] for p in g["pick_per_sem"])
    sem_labels = ", ".join(SEM_LABELS.get(p["sem"], p["sem"]) + f" 택{p['pick']}" for p in g["pick_per_sem"])
    st.markdown(f"**[{g['id']}] {sem_labels}** · 총 {g.get('total_credit','-')}학점 (정확히 {pick_total}과목 선택)")

    if len(g["pick_per_sem"]) >= 1:
        for pinfo in g["pick_per_sem"]:
            sem = pinfo["sem"]
            # 💡 연간 선택 레이블 분기 처리
            label = "3학년 제2외국어 선택 (연간 1과목)" if sem == "3-annual" else SEM_LABELS.get(sem, sem)
            
            # 단일 선택(selectbox) 로직
            if pinfo["pick"] == 1:
                options = ["(선택 안 함)"] + [s["name"] for s in subs]
                key = f"groupsel_{g['id']}_{sem}"
                current_choice = st.session_state.get(key, "(선택 안 함)")
                
                choice = st.selectbox(f"  {label} (택1)", options, key=key, index=options.index(current_choice) if current_choice in options else 0)
                
                # 기존 선택 초기화 및 업데이트
                for s in subs: selected.discard(s["id"])
                if choice != "(선택 안 함)":
                    for s in subs:
                        if s["name"] == choice:
                            selected.add(s["id"])
            # 다중 선택(checkbox) 로직
            else:
                st.caption(f"※ 아래에서 정확히 **{pinfo['pick']}과목** 체크하세요.")
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
                            val = st.checkbox(f"{s['name']} ({s.get('op_credit')}학점)", value=(s["id"] in selected), key=key)
                            if val: selected.add(s["id"])
                            else: selected.discard(s["id"])
                
                in_sel = [s for s in subs if s["id"] in selected]
                if len(in_sel) == pinfo["pick"]: st.success(f"✅ {len(in_sel)}/{pinfo['pick']}과목 선택 완료")
                elif len(in_sel) > pinfo["pick"]: st.error(f"❌ 선택 초과 ({len(in_sel)-pinfo['pick']}개 줄여주세요)")
                elif len(in_sel) > 0: st.warning(f"⚠️ {pinfo['pick']-len(in_sel)}과목 더 선택해주세요")

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
            if s["section"]=="학생선택":
                g = next((g for g in curriculum["groups"] if sid in g["subject_ids"]),None)
                if g:
                    sem = g["pick_per_sem"][0]["sem"]
                    sem_key = "3-1" if sem == "3-annual" else sem
                    by_sem[sem_key] = by_sem.get(sem_key,0) + c
            by_type[s.get("type","")] = by_type.get(s.get("type",""),0) + c

    grand = total_credit + 18

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("교과 이수학점", f"{total_credit}", delta=f"목표 174")
    c2.metric("창의적 체험활동", "18", delta="6학기×3")
    c3.metric("총 이수학점", f"{grand}", delta=f"졸업요건 192")
    c4.metric("선택 과목 수", f"{len([s for s in curriculum['subjects'] if s['id'] in final_ids])}")

    st.markdown("#### 📐 교과 영역별 충족 여부")
    req_data = []
    for a, info in curriculum["area_requirements"].items():
        got = by_area.get(a, 0)
        req = info.get("required") or 0
        status = "✅" if got >= req else "❌"
        req_data.append({"교과(군)": a, "이수학점": got, "필수학점": req, "달성률": f"{(got/req*100) if req else 0:.0f}%", "상태": status})
    st.dataframe(req_data, use_container_width=True, hide_index=True)

    issues = []
    for g in curriculum["groups"]:
        if st.session_state.entry_year == 2025 and any(gid in g["id"] for gid in ["G01", "G02", "G03"]):
            continue
            
        picked = sum(1 for sid in g["subject_ids"] if sid in picked_ids)
        target = sum(p["pick"] for p in g["pick_per_sem"])
        if picked != target:
            issues.append(f"묶음 {g['id']}: {picked}/{target}과목 선택")
            
    if not issues and total_credit >= 174:
        st.markdown("<div class='alert-success'>🎉 <b>설계 완료!</b> 선택한 모든 묶음과 영역별 이수 학점을 만족합니다.</div>", unsafe_allow_html=True)
    elif issues:
        msg = "<div class='alert-warning'><b>아래 항목을 확인해주세요:</b><ul>"
        for i in issues: msg += f"<li>{i}</li>"
        msg += "</ul></div>"
        st.markdown(msg, unsafe_allow_html=True)

# ----------------- 페이지: 2028 대입 권장 -----------------
def page_career():
    st.markdown("## 🎓 2028 대입 권장 과목 안내")
    if not career:
        st.info("진로 계열 데이터가 없습니다.")
        return
    tracks = list(career.keys())
    selected = st.selectbox("진로 계열 선택", tracks)
    info = career[selected]

    st.markdown(f"### {selected}")
    st.markdown(f"**개요:** {info['summary']}")
    st.markdown(f"**탐구과목 안내:** {info['탐구과목_안내']}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### ⭐ 필수 권장")
        for n in info["필수권장"]:
            offered = any(s["name"]==n or n in s["name"] for s in curriculum["subjects"])
            st.markdown(f"- {'🟢' if offered else '⚪'} {n}")
    with c2:
        st.markdown("#### ✨ 우대 / 추가 권장")
        for n in info["우대"]:
            offered = any(s["name"]==n or n in s["name"] for s in curriculum["subjects"])
            st.markdown(f"- {'🟢' if offered else '⚪'} {n}")
    st.caption("🟢 = 본교 개설 과목 / ⚪ = 본교 미개설 (자기주도학습/외부수업 등 보완)")
    render_made_by()

# ----------------- 페이지: 결과 출력 (워드/PDF) -----------------
def page_print():
    st.markdown("## 🖨️ 결과 출력 (학부모 상담용)")
    st.caption("시뮬레이터에서 선택한 결과를 바탕으로 상담용 보고서를 생성합니다.")

    yr_key = str(year)
    picked = st.session_state.selected_subjects.get(yr_key, set())
    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}
    final = picked | auto

    name = st.text_input("학생 이름 (선택사항)", "")
    sclass = st.text_input("학번/반 (선택사항)", "")
    counselor = st.text_input("담임/상담교사 (선택사항)", "")

    if st.button("📄 보고서 생성", type="primary"):
        html = build_report_html(name, sclass, counselor, final)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 Word로 다운로드 (.doc)", data=html.encode('utf-8-sig'), file_name=f"신선여고_{year}입학_이수계획_{name or 'student'}.doc", mime="application/msword", use_container_width=True)
        with c2:
            st.download_button("📥 HTML 다운로드", data=html.encode('utf-8'), file_name=f"신선여고_{year}입학_이수계획_{name or 'student'}.html", mime="text/html", use_container_width=True)
        with c3:
            rows = ["영역,유형,과목명,학점,학기,구분"]
            for sid in sorted(final):
                s = next((x for x in curriculum["subjects"] if x["id"]==sid), None)
                if not s: continue
                sems = ";".join(f"{x['sem']}({x['credit']})" for x in s.get("semesters",[]))
                if not sems:
                    g = next((g for g in curriculum["groups"] if sid in g["subject_ids"]),None)
                    sems = g["pick_per_sem"][0]["sem"] if g else ""
                rows.append(f'"{s["area"]}","{s.get("type","")}","{s["name"]}",{s.get("op_credit","")},"{sems}","{s["section"]}"')
            csv = "\n".join(rows)
            st.download_button("📥 CSV 다운로드 (엑셀용)", data=csv.encode("utf-8-sig"), file_name=f"신선여고_{year}입학_이수계획_{name or 'student'}.csv", mime="text/csv", use_container_width=True)
            
        st.markdown("---")
        st.info("💡 **PDF로 저장하는 방법:** 브라우저에서 **인쇄(Ctrl+P)**를 누른 뒤 대상을 **'PDF로 저장'**으로 선택하시면 표와 디자인이 유지된 깔끔한 PDF를 얻으실 수 있습니다!")
        st.markdown("### 미리보기")
        st.components.v1.html(html, height=900, scrolling=True)
    render_made_by()

def build_report_html(name, sclass, counselor, final_ids):
    subs = [s for s in curriculum["subjects"] if s["id"] in final_ids]
    by_sem = defaultdict(list)
    for s in subs:
        if s.get("semesters"):
            for sem in s["semesters"]:
                sem_key = "3-1" if sem["sem"] == "3-annual" else sem["sem"]
                by_sem[sem_key].append((s, sem["credit"]))
        else:
            g = next((g for g in curriculum["groups"] if s["id"] in g["subject_ids"]),None)
            sem = g["pick_per_sem"][0]["sem"] if g else "?"
            sem_key = "3-1" if sem == "3-annual" else sem
            by_sem[sem_key].append((s, s.get("op_credit") or 0))

    rows_html = ""
    grand_total = 0
    for sem in ["1-1","1-2","2-1","2-2","3-1","3-2"]:
        items = by_sem.get(sem, [])
        sem_total = sum(c for _,c in items)
        grand_total += sem_total
        rows_html += f"<tr><td colspan='5' class='sem-hd'>{SEM_LABELS.get(sem, sem)} · 교과 {sem_total}학점 + 창체 3학점 = {sem_total+3}학점</td></tr>"
        for s, c in items:
            rows_html += f"<tr><td>{s['area']}</td><td>{s.get('type','')}</td><td>{s['name']}</td><td>{c}</td><td>{'필수' if s['section']=='학교지정' else '선택'}</td></tr>"

    html = f"""<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head><meta charset='utf-8'><title>신선여고 이수계획 - {name}</title>
<style>
body {{ font-family: 'Malgun Gothic', sans-serif; padding: 30px; color: #111; }}
h1 {{ color: #4f46e5; }}
.info {{ background:#f9fafb; padding:14px; border-radius:8px; margin-bottom:20px; }}
table {{ width:100%; border-collapse: collapse; margin-top: 14px; }}
th, td {{ border:1px solid #d1d5db; padding:8px; font-size: 13px; text-align: left; }}
th {{ background:#eef2ff; }}
.sem-hd {{ background:#fef3c7; font-weight: 700; }}
.total {{ font-size: 18px; font-weight: 700; margin-top: 16px; color:#4f46e5; }}
</style></head><body>
<h1>🎓 신선여자고등학교 고교학점제 이수계획서</h1>
<div class='info'>
<p><b>입학년도:</b> {year}학년도 &nbsp;&nbsp; <b>학생:</b> {name or '_______'} &nbsp;&nbsp; <b>학번/반:</b> {sclass or '_______'} &nbsp;&nbsp; <b>상담교사:</b> {counselor or '_______'}</p>
</div>
<h2>이수 과목 (학기별)</h2>
<table><thead><tr><th>교과(군)</th><th>유형</th><th>과목명</th><th>학점</th><th>구분</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<div class='total'>총 교과 이수학점: {grand_total} + 창의적 체험활동 18 = <b>{grand_total + 18}학점</b> / 졸업요건 192학점</div>
</body></html>"""
    return html

# ---------------- 라우팅 ----------------
if not st.session_state.get("year_selected", False):
    page_landing()
else:
    PAGES = {
        "🏠 홈": page_home, 
        "🗺️ 핵심 이수 경로": page_core_path, 
        "📚 학년별 교과목 탐색": page_explore, 
        "📅 시간표 시뮬레이터": page_simulator, 
        "🎓 2028 대입 권장 과목": page_career, 
        "🖨️ 결과 출력": page_print
    }
    PAGES[page]()
