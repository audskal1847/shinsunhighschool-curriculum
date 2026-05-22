import streamlit as st
import json, os
from pathlib import Path

st.set_page_config(
    page_title="신선여자고등학교 고교학점제 이수 가이드북",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"   # ⭐ 로고 폴더

# ----------------- 공용 로더 -----------------
@st.cache_data
def load_curriculum(year: int):
    path = DATA_DIR / f"curriculum_{year}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_career():
    with open(DATA_DIR / "career_recommendations.json", "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_teacher_comments():
    with open(DATA_DIR / "teacher_comments.json", "r", encoding="utf-8") as f:
        return json.load(f)

# ----------------- CSS -----------------
st.markdown("""
<style>
.big-card {
    background: linear-gradient(135deg, #f8faff 0%, #eef2ff 100%);
    border: 1px solid #e0e7ff;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.2s;
    height: 100%;
}
.big-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(99,102,241,.15); }
.big-card h2 {
    background: linear-gradient(90deg, #4f46e5, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 56px; margin: 0; font-weight: 800;
}
.big-card p { color: #4b5563; margin: 8px 0 0 0; }
.big-card .sub { color: #6b7280; font-size: 13px; margin-top: 4px; }

.subject-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: all 0.15s;
}
.subject-card:hover { border-color: #6366f1; box-shadow: 0 4px 12px rgba(99,102,241,.08); }
.badge {
    display:inline-block; padding: 2px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 600; margin-right: 4px;
}
.badge-area { background: #f3f4f6; color: #374151; }
.badge-type-공통 { background: #dbeafe; color: #1e40af; }
.badge-type-일반 { background: #ede9fe; color: #5b21b6; }
.badge-type-진로 { background: #fef3c7; color: #92400e; }
.badge-type-융합 { background: #fce7f3; color: #9d174d; }
.badge-req { background: #dcfce7; color: #166534; }
.badge-sel { background: #fef9c3; color: #854d0e; }
.title-gradient {
    background: linear-gradient(90deg, #4f46e5 0%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}
.metric-box {
    background: #f9fafb; border-left: 4px solid #6366f1;
    padding: 12px 16px; border-radius: 8px; margin: 4px 0;
}
.alert-success { background:#f0fdf4; border-left:4px solid #22c55e; padding:12px; border-radius:8px; }
.alert-warning { background:#fffbeb; border-left:4px solid #f59e0b; padding:12px; border-radius:8px; }
.alert-error { background:#fef2f2; border-left:4px solid #ef4444; padding:12px; border-radius:8px; }

/* ⭐ 랜딩 페이지 전용 스타일 */
.landing-title-pink {
    color: #f4a8b8;
    font-size: 48px;
    font-weight: 900;
    margin: 0;
    letter-spacing: -1px;
}
.landing-title-black {
    color: #1f2937;
    font-size: 46px;
    font-weight: 900;
    margin: 8px 0 0 0;
    letter-spacing: -1px;
}
.landing-year {
    color: #c4a8e8;
    font-size: 48px;
    font-weight: 900;
    margin: 0;
    letter-spacing: -2px;
    line-height: 1.2;
    text-align: center;
}
.landing-year-sub {
    color: #6b7280;
    font-size: 18px;
    margin: 12px 0 0 0;
    text-align: center;
}
    /* Primary 버튼 글씨 크게 + 굵게 */
    .stButton > button[kind="primary"] {
        font-size: 30px !important;
        font-weight: 900 !important;
        padding: 18px 28px !important;
        letter-spacing: -0.3px !important;
    }
    .stButton > button[kind="primary"] p {
        font-size: 22px !important;
        font-weight: 900 !important;
    }

</style>
""", unsafe_allow_html=True)

# ----------------- 세션 상태 초기화 -----------------
if "entry_year" not in st.session_state:
    st.session_state.entry_year = 2025

if "year_selected" not in st.session_state:
    st.session_state.year_selected = False

if "selected_subjects" not in st.session_state:    # ⭐ 시뮬레이터용 추가
    st.session_state.selected_subjects = {}


# ----------------- 사이드바 -----------------
with st.sidebar:
   # 기존 146번째 줄(학교 이름)은 삭제합니다.
    st.markdown(
    "<p style='font-size: 22px; color: #555555;'>⭐주체적인 삶의 주인공으로 거듭나는 신선여고인을 응원합니다.</p>", 
    unsafe_allow_html=True
)
    st.markdown("---")

    # ⭐ 학년도가 선택된 경우에만 메뉴 표시
    if st.session_state.get("year_selected", False):
        year = st.radio(
            "입학년도 선택",
            [2025, 2026],
            format_func=lambda y: f"{y}학년도 입학생 ({'현재 2학년' if y==2025 else '현재 1학년'})",
            index=0 if st.session_state.entry_year != 2026 else 1,
            key="year_radio",
        )
        st.session_state.entry_year = year

        st.markdown("---")

        page = st.radio(
            "메뉴",
            ["🏠 홈", "🗺️ 핵심 이수 경로", "📚 학년별 교과목 탐색",
             "📅 시간표 시뮬레이터", "🎓 2028 대입 권장 과목", "📄 결과 출력"],
            key="page_radio",
        )
    else:
        st.info("👉 가장 먼저 입학년도를 선택해야 다음 기능을 사용할 수 있습니다.")
        page = None
        year = st.session_state.get("entry_year", 2025)


# ⭐ 데이터 로드 (한 번만!)
curriculum = load_curriculum(year)
career = load_career()
comments = load_teacher_comments()

SEM_LABELS = {"1-1":"1학년 1학기","1-2":"1학년 2학기",
              "2-1":"2학년 1학기","2-2":"2학년 2학기",
              "3-1":"3학년 1학기","3-2":"3학년 2학기"}

# ---------------- 공통 푸터: 만든 이 ----------------
def render_made_by():
    st.markdown(
        """
        <div style='text-align: center; padding: 24px 0 16px 0; 
                    border-top: 1px solid #e5e7eb; margin-top: 40px;'>
            <p style='font-size: 20px; margin: 0; line-height: 1.6;'>
                <span style='color: #111827; font-weight: 800;'>만든 이:</span>
                <span style='color: #4b5563; font-weight: 600; margin-left: 6px;'>
                    신선여자고등학교 교육과정부 &amp; 교무부
                </span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
# ---------------- 페이지: 랜딩 (입학년도 선택) ----------------
def page_landing():
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

            # 로고 + 학교명 영역 (중앙 정렬)
    pad_l, col_logo, col_title, pad_r = st.columns([2, 1.5, 2.5, 1.5], gap="small")

    with col_logo:
        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=260)
        else:
            st.markdown(
                "<div style='text-align:center; font-size:160px; line-height:1;'>🎓</div>",
                unsafe_allow_html=True,
            )

    with col_title:
        st.markdown(
            """
            <div style='padding: 50px 0 0 0;'>
                <h1 class='landing-title-pink'>신선여자고등학교</h1>
                <h2 class='landing-title-black'>고교학점제 이수 가이드</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )


    # 안내 문구
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style='text-align: center; color: #1f2937; 
                  font-size: 28px; font-weight: 600; margin: 0;'>
            * 입학년도를 선택하세요.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

        # 학년도 선택 카드 (2개)
    col_pad_l, col1, col_mid, col2, col_pad_r = st.columns([1, 3, 0.5, 3, 1])

    with col1:
        if st.button("2025학년도 입학생 선택 (현재 2학년)", 
                     key="landing_btn_2025", 
                     use_container_width=True,
                     type="primary"):
            st.session_state.entry_year = 2025
            st.session_state.year_selected = True
            st.rerun()

    with col2:
        if st.button("2026학년도 입학생 선택 (현재 1학년)", 
                     key="landing_btn_2026", 
                     use_container_width=True,
                     type="primary"):
            st.session_state.entry_year = 2026
            st.session_state.year_selected = True
            st.rerun()
    render_made_by()
# ---------------- 페이지: 홈 ----------------
def page_home():
    # ⭐ 상단: 학년도 변경 버튼 (우측 정렬)
    col_l, col_r = st.columns([5, 1])
    with col_r:
        if st.button("🔄 학년도 변경", use_container_width=True, key="btn_change_year"):
            st.session_state.year_selected = False
            st.rerun()

    # 메인 타이틀
    st.markdown(
        f"<h1><span class='title-gradient'>{year}학년도 입학생</span><br>고교학점제 이수 가이드북</h1>",
        unsafe_allow_html=True,
    )
    st.caption("성공적인 고교학점제 마무리를 위한 진로 학업 설계 가이드북")
    st.markdown("")

    # 메트릭 카드 3개
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class='big-card'><h2>192</h2><p>졸업 필수 학점</p><span class='sub'>교과 174 + 창체 18</span></div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class='big-card'><h2>122</h2><p>학교지정 학점</p><span class='sub'>필수 이수 (40과목)</span></div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class='big-card'><h2>52</h2><p>학생선택 학점</p><span class='sub'>택 18과목</span></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📖 이 가이드북 사용법")
    st.markdown("""
1. **🗺️ 핵심 이수 경로** — 졸업까지 반드시 이수해야 하는 영역과 학점을 확인하세요.
2. **📚 학년별 교과목 탐색** — 학년·학기별 과목 카드를 살펴보세요.
3. **📅 시간표 시뮬레이터 ⭐** — **직접 과목을 체크**해보고 졸업 요건 충족 여부를 확인할 수 있어요.
4. **🎓 2028 대입 권장 과목** — 진로 계열별 추천 과목을 안내합니다.
5. **📄 결과 출력** — 시뮬레이션 결과를 PDF/HTML로 저장해 상담 자료로 활용하세요.
""")

    render_made_by()
# ----------------- 페이지: 핵심 이수 경로 -----------------
def page_core_path():
    st.markdown("## 🗺️ 핵심 이수 경로")
    st.caption("졸업까지 반드시 이수해야 하는 필수 영역과 학점입니다.")

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
            req = 0
            total = 0
            for a in area_list:
                if a in areas:
                    if areas[a].get("required"):
                        req += areas[a]["required"]
                    if areas[a].get("total"):
                        total += areas[a]["total"]
            
            # 기술/교양/제2외국어 공동 합계 예외 처리
            if "공동 합계" in str([areas[a].get("note","") for a in area_list if a in areas]):
                total = areas[area_list[0]].get("total") or 0
                req = areas[area_list[0]].get("required") or 0
            
            req_str = req if req > 0 else "-"
            
            st.markdown(f"""
            <div class='subject-card' style='min-height:140px'>
              <div style='font-weight:700; font-size:16px; margin-bottom:6px'>{title}</div>
              <div style='color:#4f46e5; font-weight:600'>필수 {req_str}학점 · 총 운영 {total}학점</div>
              <div style='color:#6b7280; font-size:13px; margin-top:8px'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 영역별 상세 학점")
    rows = []
    for a, info in areas.items():
        rows.append({
            "교과(군)": a,
            "총 운영학점": info.get("total"),
            "필수 이수학점": info.get("required"),
            "비고": info.get("note","")
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.info("💡 **학년별 학기당 이수학점**: 1학년 31학점 / 2학년 30학점 / 3학년 26학점 + 창의적 체험활동 학기당 3학점")


# ----------------- 페이지: 학년별 교과목 탐색 -----------------
def page_explore():
    st.markdown("## 📚 학년별 교과목 탐색")
    st.caption("학년을 선택하면 학기별 개설 과목을 카드로 볼 수 있습니다.")

    tab1, tab2, tab3 = st.tabs(["1학년", "2학년", "3학년"])
    for tab, grade in [(tab1,1),(tab2,2),(tab3,3)]:
        with tab:
            sem_cols = st.columns(2)
            for idx, sem_num in enumerate([1,2]):
                sem_key = f"{grade}-{sem_num}"
                with sem_cols[idx]:
                    st.markdown(f"#### 📅 {grade}학년 {sem_num}학기")
                    show_semester_subjects(sem_key)


def show_semester_subjects(sem_key):
    subs = []
    for s in curriculum["subjects"]:
        for sem in s.get("semesters", []):
            if sem["sem"] == sem_key:
                subs.append((s, sem["credit"]))
                break
        else:
            for n in s.get("notes", []):
                if n["sem"] == sem_key:
                    subs.append((s, s.get("op_credit") or 0))
                    break

    required = [(s,c) for (s,c) in subs if s["section"]=="학교지정"]
    selective = [(s,c) for (s,c) in subs if s["section"]=="학생선택"]

    if required:
        with st.expander(f"✅ 필수 이수 과목 ({len(required)}과목)", expanded=True):
            for s, c in required:
                render_subject_card(s, c)
    if selective:
        from collections import defaultdict
        gmap = defaultdict(list)
        for s, c in selective:
            gmap[s["group_id"]].append((s,c))
        for gid, items in gmap.items():
            g = next((g for g in curriculum["groups"] if g["id"]==gid), None)
            pick_label = ""
            if g:
                picks = [p for p in g["pick_per_sem"] if p["sem"]==sem_key]
                if picks:
                    pick_label = f" (택{picks[0]['pick']})"
            with st.expander(f"🔵 학생선택 묶음 {gid}{pick_label} · {len(items)}과목 중 선택", expanded=False):
                if g:
                    st.caption(f"이 묶음의 총 이수학점: **{g.get('total_credit')}학점**")
                for s, c in items:
                    render_subject_card(s, c)


def render_subject_card(s, sem_credit=None):
    credit = sem_credit if sem_credit else s.get("op_credit") or 0
    typ = s.get("type","")
    badge_cls = f"badge-type-{typ}" if typ in ("공통","일반","진로","융합") else "badge-area"
    req_badge = "<span class='badge badge-req'>필수</span>" if s["section"]=="학교지정" else "<span class='badge badge-sel'>선택</span>"
    yrk = str(curriculum["entry_year"])
    tc = comments.get(yrk, {}).get(s["name"], None)
    tc_html = ""
    if tc and tc.get("comment"):
        tc_html = f"<div style='margin-top:6px; padding:8px; background:#f9fafb; border-radius:6px; font-size:12px; color:#4b5563'>💬 {tc['comment']}</div>"
    st.markdown(f"""
    <div class='subject-card'>
      <div style='display:flex; justify-content:space-between; align-items:center'>
        <div>
          <span class='badge badge-area'>{s['area']}</span>
          <span class='badge {badge_cls}'>{typ}</span>
          {req_badge}
        </div>
        <div style='color:#4f46e5; font-weight:700'>{credit}학점</div>
      </div>
      <div style='font-size:16px; font-weight:600; margin-top:8px'>{s['name']}</div>
      {tc_html}
    </div>
    """, unsafe_allow_html=True)


# ----------------- 페이지: 시뮬레이터 -----------------
def page_simulator():
    st.markdown("## 🧮 나의 시간표 시뮬레이터")
    st.caption("학교지정 과목은 자동으로 포함됩니다. 학생선택 묶음에서 정확히 정해진 개수만큼 선택하세요.")

    yr_key = str(year)
    if yr_key not in st.session_state.selected_subjects:
        st.session_state.selected_subjects[yr_key] = set()
    selected = st.session_state.selected_subjects[yr_key]

    auto = set()
    for s in curriculum["subjects"]:
        if s["section"]=="학교지정" and s["group_id"] is None:
            auto.add(s["id"])

    st.markdown("### 🔵 학생선택 묶음 (그룹별 택N)")
    for g in curriculum["groups"]:
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


def render_group_picker(g, selected):
    subs = [s for s in curriculum["subjects"] if s["id"] in g["subject_ids"]]
    pick_total = sum(p["pick"] for p in g["pick_per_sem"])
    sem_labels = ", ".join(SEM_LABELS.get(p["sem"],"") + f" 택{p['pick']}" for p in g["pick_per_sem"])
    st.markdown(f"**[{g['id']}] {sem_labels}** · 총 {g.get('total_credit','-')}학점 (정확히 {pick_total}과목 선택)")

    if len(g["pick_per_sem"]) > 1:
        for pi, pinfo in enumerate(g["pick_per_sem"]):
            sem = pinfo["sem"]
            options = ["(선택 안 함)"] + [s["name"] for s in subs]
            current_idx = 0
            for i, s in enumerate(subs):
                if s["id"] in selected:
                    key_tracker = f"groupsel_{g['id']}_{sem}"
                    if st.session_state.get(key_tracker) == s["name"]:
                        current_idx = i + 1
            key = f"groupsel_{g['id']}_{sem}"
            choice = st.selectbox(f"  {SEM_LABELS.get(sem)} (택{pinfo['pick']})", options, key=key, index=current_idx)
    else:
        pinfo = g["pick_per_sem"][0]
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
                    val = st.checkbox(
                        f"{s['name']} ({s.get('op_credit')}학점)",
                        value=(s["id"] in selected),
                        key=key,
                    )
                    if val:
                        selected.add(s["id"])
                    else:
                        selected.discard(s["id"])
        in_sel = [s for s in subs if s["id"] in selected]
        if len(in_sel) == pinfo["pick"]:
            st.success(f"✅ {len(in_sel)}/{pinfo['pick']}과목 선택 완료")
        elif len(in_sel) > pinfo["pick"]:
            st.error(f"❌ {len(in_sel)}/{pinfo['pick']}과목 — 선택 초과 ({len(in_sel)-pinfo['pick']}개 줄여주세요)")
        elif len(in_sel) > 0:
            st.warning(f"⚠️ {len(in_sel)}/{pinfo['pick']}과목 — {pinfo['pick']-len(in_sel)}과목 더 선택해주세요")
        else:
            st.info(f"ℹ️ {pinfo['pick']}과목을 선택해주세요")

    if len(g["pick_per_sem"]) > 1:
        ids_in_g = {s["id"] for s in subs}
        selected -= ids_in_g
        for pinfo in g["pick_per_sem"]:
            sem = pinfo["sem"]
            key = f"groupsel_{g['id']}_{sem}"
            chosen_name = st.session_state.get(key)
            if chosen_name and chosen_name != "(선택 안 함)":
                for s in subs:
                    if s["name"] == chosen_name:
                        selected.add(s["id"])
                        break
        total_chosen = sum(1 for s in subs if s["id"] in selected)
        if total_chosen == pick_total:
            st.success(f"✅ {total_chosen}/{pick_total}과목 선택 완료")
        elif total_chosen > 0:
            st.warning(f"⚠️ {total_chosen}/{pick_total}과목 — 학기별 선택을 확인하세요")


def show_summary(final_ids, auto_ids, picked_ids):
    total_credit = 0
    by_area = {}
    by_sem = {f"{g}-{s}":0 for g in (1,2,3) for s in (1,2)}
    by_type = {"공통":0,"일반":0,"진로":0,"융합":0}

    for sid in final_ids:
        s = next((x for x in curriculum["subjects"] if x["id"]==sid), None)
        if not s: continue
        c = s.get("op_credit") or 0
        if s.get("semesters"):
            for sem in s["semesters"]:
                total_credit += sem["credit"]
                by_area[s["area"]] = by_area.get(s["area"],0) + sem["credit"]
                by_sem[sem["sem"]] = by_sem.get(sem["sem"],0) + sem["credit"]
                by_type[s.get("type","")] = by_type.get(s.get("type",""),0) + sem["credit"]
        else:
            total_credit += c
            by_area[s["area"]] = by_area.get(s["area"],0) + c
            if s["section"]=="학생선택":
                g = next((g for g in curriculum["groups"] if sid in g["subject_ids"]),None)
                if g:
                    sem = g["pick_per_sem"][0]["sem"]
                    by_sem[sem] = by_sem.get(sem,0) + c
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
        req_data.append({
            "교과(군)": a,
            "이수학점": got,
            "필수학점": req,
            "달성률": f"{(got/req*100) if req else 0:.0f}%",
            "상태": status,
            "비고": info.get("note","")
        })
    st.dataframe(req_data, use_container_width=True, hide_index=True)

    st.markdown("#### 📅 학기별 이수학점")
    sem_data = []
    for k,v in by_sem.items():
        sem_data.append({"학기": SEM_LABELS.get(k,k), "교과 학점": v, "창체": 3, "합계": v+3})
    st.dataframe(sem_data, use_container_width=True, hide_index=True)

    st.markdown("#### 🎯 과목 유형별 학점 분포")
    cc1, cc2, cc3, cc4 = st.columns(4)
    cc1.metric("공통", f"{by_type.get('공통',0)}")
    cc2.metric("일반선택", f"{by_type.get('일반',0)}")
    cc3.metric("진로선택", f"{by_type.get('진로',0)}")
    cc4.metric("융합선택", f"{by_type.get('융합',0)}")

    st.markdown("---")
    st.markdown("#### 🏁 종합 판정")
    issues = []
    for g in curriculum["groups"]:
        picked = sum(1 for sid in g["subject_ids"] if sid in picked_ids)
        target = sum(p["pick"] for p in g["pick_per_sem"])
        if picked != target:
            issues.append(f"묶음 {g['id']}: {picked}/{target}과목 선택")
    for a, info in curriculum["area_requirements"].items():
        if by_area.get(a,0) < (info.get("required") or 0):
            issues.append(f"{a}: 필수 {info['required']}학점 중 {by_area.get(a,0)}학점만 이수")

    if not issues and total_credit >= 174:
        st.markdown("<div class='alert-success'>🎉 <b>졸업 요건 충족!</b> 모든 묶음과 영역별 필수 학점을 만족합니다.</div>", unsafe_allow_html=True)
    else:
        msg = "<div class='alert-warning'><b>아래 항목을 확인해주세요:</b><ul>"
        for i in issues:
            msg += f"<li>{i}</li>"
        if total_credit < 174:
            msg += f"<li>교과 총 학점이 부족합니다 ({total_credit}/174)</li>"
        msg += "</ul></div>"
        st.markdown(msg, unsafe_allow_html=True)


# ----------------- 페이지: 2028 대입 권장 -----------------
def page_career():
    st.markdown("## 🎓 2028 대입 권장 과목 안내")
    st.caption("진로계열별 권장 과목입니다. 학과/대학별로 다를 수 있으니 진학상담과 함께 활용하세요.")

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
            mark = "🟢" if offered else "⚪"
            st.markdown(f"- {mark} {n}")
    with c2:
        st.markdown("#### ✨ 우대 / 추가 권장")
        for n in info["우대"]:
            offered = any(s["name"]==n or n in s["name"] for s in curriculum["subjects"])
            mark = "🟢" if offered else "⚪"
            st.markdown(f"- {mark} {n}")

    st.caption("🟢 = 본교 개설 과목 / ⚪ = 본교 미개설 (자기주도학습/외부수업 등 보완)")


# ----------------- 페이지: 결과 출력 -----------------
def page_print():
    st.markdown("## 🖨️ 결과 출력 (학부모 상담용)")
    st.caption("시뮬레이터에서 선택한 결과를 HTML/CSV로 저장할 수 있습니다.")

    yr_key = str(year)
    picked = st.session_state.selected_subjects.get(yr_key, set())
    auto = {s["id"] for s in curriculum["subjects"] if s["section"]=="학교지정" and s["group_id"] is None}
    final = picked | auto

    name = st.text_input("학생 이름 (선택사항)", "")
    sclass = st.text_input("학번/반 (선택사항)", "")
    counselor = st.text_input("담임/상담교사 (선택사항)", "")

    if st.button("📄 보고서 생성", type="primary"):
        html = build_report_html(name, sclass, counselor, final)
        st.download_button(
            "📥 HTML 다운로드",
            data=html,
            file_name=f"신선여고_{year}입학_이수계획_{name or 'student'}.html",
            mime="text/html",
        )
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
        st.download_button(
            "📥 CSV 다운로드 (엑셀용)",
            data=csv.encode("utf-8-sig"),
            file_name=f"신선여고_{year}입학_이수계획_{name or 'student'}.csv",
            mime="text/csv",
        )
        st.markdown("---")
        st.markdown("### 미리보기")
        st.components.v1.html(html, height=900, scrolling=True)
        st.info("💡 다운로드한 HTML을 브라우저로 열어 **Ctrl+P (인쇄 → PDF로 저장)** 하면 PDF로도 보관할 수 있습니다.")


def build_report_html(name, sclass, counselor, final_ids):
    subs = [s for s in curriculum["subjects"] if s["id"] in final_ids]
    from collections import defaultdict
    by_sem = defaultdict(list)
    for s in subs:
        if s.get("semesters"):
            for sem in s["semesters"]:
                by_sem[sem["sem"]].append((s, sem["credit"]))
        else:
            g = next((g for g in curriculum["groups"] if s["id"] in g["subject_ids"]),None)
            sem = g["pick_per_sem"][0]["sem"] if g else "?"
            by_sem[sem].append((s, s.get("op_credit") or 0))

    rows_html = ""
    grand_total = 0
    for sem in ["1-1","1-2","2-1","2-2","3-1","3-2"]:
        items = by_sem.get(sem, [])
        sem_total = sum(c for _,c in items)
        grand_total += sem_total
        rows_html += f"<tr><td colspan='5' class='sem-hd'>{SEM_LABELS.get(sem)} · 교과 {sem_total}학점 + 창체 3학점 = {sem_total+3}학점</td></tr>"
        for s, c in items:
            rows_html += f"<tr><td>{s['area']}</td><td>{s.get('type','')}</td><td>{s['name']}</td><td>{c}</td><td>{'필수' if s['section']=='학교지정' else '선택'}</td></tr>"

    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>신선여고 이수계획 - {name}</title>
<style>
body {{ font-family: 'Pretendard', 'Malgun Gothic', sans-serif; padding: 30px; color: #111; }}
h1 {{ background: linear-gradient(90deg,#4f46e5,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color: transparent; }}
.info {{ background:#f9fafb; padding:14px; border-radius:8px; margin-bottom:20px; }}
.info p {{ margin: 4px 0; }}
table {{ width:100%; border-collapse: collapse; margin-top: 14px; }}
th, td {{ border:1px solid #d1d5db; padding:8px; font-size: 13px; }}
th {{ background:#eef2ff; }}
.sem-hd {{ background:#fef3c7; font-weight: 700; }}
.total {{ font-size: 18px; font-weight: 700; margin-top: 16px; color:#4f46e5; }}
@media print {{ body {{ padding: 10px; }} }}
</style></head><body>
<h1>🎓 신선여자고등학교 고교학점제 이수계획서</h1>
<div class='info'>
<p><b>입학년도:</b> {year}학년도</p>
<p><b>학생:</b> {name or '_______'} &nbsp;&nbsp; <b>학번/반:</b> {sclass or '_______'}</p>
<p><b>상담교사:</b> {counselor or '_______'}</p>
</div>
<h2>이수 과목 (학기별)</h2>
<table>
<thead><tr><th>교과(군)</th><th>유형</th><th>과목명</th><th>학점</th><th>구분</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div class='total'>총 교과 이수학점: {grand_total} + 창의적 체험활동 18 = <b>{grand_total + 18}학점</b> / 졸업요건 192학점</div>
</body></html>"""
    return html


# ---------------- 라우팅 ----------------
if not st.session_state.get("year_selected", False):
    # ⭐ 학년도 미선택 → 랜딩 페이지 표시
    page_landing()
else:
    # ⭐ 학년도 선택됨 → 일반 페이지 라우팅
    PAGES = {
        "🏠 홈": page_home,
        "🗺️ 핵심 이수 경로": page_core_path,
        "📚 학년별 교과목 탐색": page_explore,
        "📅 시간표 시뮬레이터": page_simulator,
        "🎓 2028 대입 권장 과목": page_career,
        "📄 결과 출력": page_print,
    }
    PAGES[page]()
