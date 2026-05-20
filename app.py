import streamlit as st
import json
from pathlib import Path

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="신선여고 고교학점제 이수 가이드북",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"


# ─────────────────────────────────────────────
# 데이터 로더
# ─────────────────────────────────────────────
@st.cache_data
def load_curriculum(year: int):
    path = DATA_DIR / f"curriculum_{year}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_career():
    path = DATA_DIR / "career_recommendations.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_teacher_comments():
    path = DATA_DIR / "teacher_comments.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# 공통 사이드바 푸터 (제작자 정보)
# ─────────────────────────────────────────────
def render_sidebar_footer():
    """사이드바 하단에 제작자 정보 카드 표시"""
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='
            background: linear-gradient(135deg, #f3f4f6 0%, #e0e7ff 100%);
            border-left: 4px solid #2563eb;
            border-radius: 8px;
            padding: 12px 14px;
            margin-top: 10px;
        '>
            <p style='font-size: 11px; color: #6b7280; margin: 0 0 4px 0; letter-spacing: 0.5px;'>
                MADE BY
            </p>
            <p style='font-weight: 800; font-size: 14px; color: #1e3a8a; margin: 0; line-height: 1.4;'>
                신선여자고등학교<br>
                교육과정부 &amp; 교무부
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 사이드바 (입학년도 + 페이지 선택)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 신선여고")
    st.markdown("### 고교학점제 가이드북")
    st.markdown("---")

    year = st.radio(
        "📅 입학년도 선택",
        [2025, 2026],
        format_func=lambda y: f"{y}학년도 입학생 ({'현재 2학년' if y == 2025 else '현재 1학년'})",
    )

    st.markdown("---")

    page = st.radio(
        "📂 메뉴",
        [
            "🏠 홈",
            "🗺️ 핵심 이수 경로",
            "📚 학년별 교과목 탐색",
            "🧮 시간표 시뮬레이터",
            "🎯 진로계열별 권장 과목",
            "📄 결과 출력",
        ],
    )

# 사이드바 하단 제작자 정보
render_sidebar_footer()


# ─────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────
curriculum = load_curriculum(year)
career = load_career()
comments = load_teacher_comments()


# ─────────────────────────────────────────────
# 페이지 1: 홈
# ─────────────────────────────────────────────
def page_home():
    st.markdown(
        f"""
        <div style='text-align:center; padding: 30px 0 20px 0;'>
            <h1 style='background: linear-gradient(90deg, #2563eb, #a855f7);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size: 42px; font-weight: 900; margin: 0;'>
                {year}학년도 입학생
            </h1>
            <h2 style='color: #1f2937; font-size: 28px; margin-top: 8px;'>
                고교학점제 이수 가이드북
            </h2>
            <p style='color: #6b7280; margin-top: 16px;'>
                좌측 메뉴에서 원하는 기능을 선택하세요
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("졸업 필수 학점", f"{curriculum.get('graduation_credits', 192)}학점")
    with col2:
        total_subjects = sum(
            len(s.get("subjects", []))
            for g in curriculum.get("grades", [])
            for s in g.get("semesters", [])
        )
        st.metric("개설 과목 수", f"{total_subjects}개")
    with col3:
        st.metric("입학년도", f"{year}학년도")

    st.markdown("---")
    st.markdown("### 🧭 이용 안내")
    st.info(
        """
        - **🗺️ 핵심 이수 경로**: 교과 영역별로 반드시 이수해야 하는 학점을 안내합니다.
        - **📚 학년별 교과목 탐색**: 학년·학기별 개설 과목을 카드 형태로 확인합니다.
        - **🧮 시간표 시뮬레이터**: 직접 과목을 선택하여 졸업 요건 충족 여부를 검증합니다.
        - **🎯 진로계열별 권장 과목**: 의약학·이공·인문 등 진로별 추천 과목을 안내합니다.
        - **📄 결과 출력**: 시뮬레이션 결과를 상담용으로 출력합니다.
        """
    )


# ─────────────────────────────────────────────
# 페이지 2: 핵심 이수 경로
# ─────────────────────────────────────────────
def page_core_path():
    st.markdown("## 🗺️ 핵심 이수 경로")
    st.caption("반드시 이수해야 하는 필수 영역의 로드맵입니다.")

    requirements = curriculum.get("area_requirements", [])
    if not requirements:
        st.warning("영역별 필수 학점 데이터가 없습니다.")
        return

    cols = st.columns(3)
    for i, req in enumerate(requirements):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style='border: 1px solid #e5e7eb; border-radius: 12px;
                            padding: 20px; margin-bottom: 16px;
                            background: #ffffff;'>
                    <h4 style='margin: 0; color: #1f2937;'>{req.get('icon', '📘')} {req['area']}</h4>
                    <p style='color: #6b7280; font-size: 13px; margin: 8px 0;'>
                        필수 {req['required_credits']}학점
                    </p>
                    <p style='color: #374151; font-size: 14px; margin: 0;'>
                        {req.get('description', '')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# 페이지 3: 학년별 교과목 탐색
# ─────────────────────────────────────────────
def page_explore():
    st.markdown("## 📚 학년별 교과목 탐색")
    st.caption("과목 카드를 클릭하여 담당 교사의 상세 코멘트와 선택 조건을 확인하세요.")

    grades = curriculum.get("grades", [])
    if not grades:
        st.warning("교육과정 데이터가 없습니다.")
        return

    tabs = st.tabs([f"{g['grade']}학년" for g in grades])

    for tab, grade in zip(tabs, grades):
        with tab:
            for sem in grade.get("semesters", []):
                st.markdown(
                    f"### 📅 {grade['grade']}학년 {sem['semester']}학기 "
                    f"<span style='color:#6b7280; font-size: 14px;'>"
                    f"(배정 과목 수: {len(sem.get('subjects', []))}개)</span>",
                    unsafe_allow_html=True,
                )

                required = [s for s in sem.get("subjects", []) if s.get("type") == "필수"]
                elective = [s for s in sem.get("subjects", []) if s.get("type") != "필수"]

                if required:
                    st.markdown(f"#### ✅ 필수 이수 과목 ({len(required)}과목)")
                    show_subject_cards(required)

                if elective:
                    st.markdown(f"#### 🎨 학생 선택 과목 ({len(elective)}과목)")
                    show_subject_cards(elective)


def show_subject_cards(subjects):
    cols = st.columns(3)
    for i, subj in enumerate(subjects):
        with cols[i % 3]:
            comment = comments.get(subj["name"], "")
            comment_badge = "💬 " if comment else ""
            with st.expander(f"{comment_badge}{subj['name']} ({subj['credits']}학점)"):
                st.markdown(f"- **교과**: {subj.get('category', '-')}")
                st.markdown(f"- **이수구분**: {subj.get('classification', '-')}")
                st.markdown(f"- **학점**: {subj['credits']}학점")
                if subj.get("group_id"):
                    st.markdown(f"- **선택 그룹**: {subj['group_id']}")
                if comment:
                    st.info(f"💬 **담당 교사 코멘트**\n\n{comment}")


# ─────────────────────────────────────────────
# 페이지 4: 시간표 시뮬레이터
# ─────────────────────────────────────────────
def page_simulator():
    st.markdown("## 🧮 나만의 시간표 시뮬레이터")
    st.caption("과목을 선택하면 졸업 요건 충족 여부를 실시간으로 확인할 수 있습니다.")

    if "selected_subjects" not in st.session_state:
        st.session_state.selected_subjects = {}

    grades = curriculum.get("grades", [])

    for grade in grades:
        with st.expander(f"📖 {grade['grade']}학년", expanded=(grade["grade"] == 1)):
            for sem in grade.get("semesters", []):
                st.markdown(f"#### {grade['grade']}학년 {sem['semester']}학기")

                # 필수 과목 자동 체크
                required = [s for s in sem.get("subjects", []) if s.get("type") == "필수"]
                if required:
                    st.markdown("**✅ 필수 과목 (자동 선택)**")
                    for s in required:
                        st.session_state.selected_subjects[s["name"]] = True
                        st.markdown(f"- {s['name']} ({s['credits']}학점)")

                # 선택 그룹별
                groups = {}
                for s in sem.get("subjects", []):
                    if s.get("type") != "필수":
                        gid = s.get("group_id", "기타")
                        groups.setdefault(gid, []).append(s)

                for gid, subjects in groups.items():
                    pick = subjects[0].get("pick_count", 1) if subjects else 1
                    st.markdown(f"**🎨 {gid} (택{pick})**")

                    selected_in_group = []
                    for s in subjects:
                        key = f"{grade['grade']}_{sem['semester']}_{s['name']}"
                        checked = st.checkbox(
                            f"{s['name']} ({s['credits']}학점)",
                            key=key,
                            value=st.session_state.selected_subjects.get(s["name"], False),
                        )
                        st.session_state.selected_subjects[s["name"]] = checked
                        if checked:
                            selected_in_group.append(s["name"])

                    if len(selected_in_group) != pick:
                        st.warning(
                            f"⚠️ {pick}과목을 선택해야 합니다. (현재 {len(selected_in_group)}개 선택됨)"
                        )
                    else:
                        st.success(f"✅ {pick}과목 선택 완료")

    # 학점 요약
    st.markdown("---")
    st.markdown("### 📊 학점 요약")
    total = 0
    for grade in grades:
        for sem in grade.get("semesters", []):
            for s in sem.get("subjects", []):
                if st.session_state.selected_subjects.get(s["name"]):
                    total += s["credits"]

    target = curriculum.get("graduation_credits", 192)
    col1, col2, col3 = st.columns(3)
    col1.metric("선택 학점", f"{total}학점")
    col2.metric("졸업 요건", f"{target}학점")
    col3.metric("달성률", f"{round(total/target*100, 1)}%")

    st.progress(min(total / target, 1.0))


# ─────────────────────────────────────────────
# 페이지 5: 진로계열별 권장 과목
# ─────────────────────────────────────────────
def page_career():
    st.markdown("## 🎯 진로계열별 권장 과목")
    st.caption("2028 대입을 대비한 계열별 추천 과목입니다.")

    if not career:
        st.warning("진로 권장 과목 데이터가 없습니다.")
        return

    tracks = list(career.keys())
    selected = st.selectbox("진로 계열 선택", tracks)

    info = career[selected]
    st.markdown(f"### {info.get('icon', '🎓')} {selected}")
    st.write(info.get("description", ""))

    st.markdown("#### 📌 권장 과목")
    for subj in info.get("recommended", []):
        st.markdown(f"- **{subj['name']}** — {subj.get('reason', '')}")


# ─────────────────────────────────────────────
# 페이지 6: 결과 출력
# ─────────────────────────────────────────────
def page_export():
    st.markdown("## 📄 결과 출력")
    st.caption("시뮬레이션 결과를 학부모 상담용으로 출력할 수 있습니다.")

    selected = [
        name for name, v in st.session_state.get("selected_subjects", {}).items() if v
    ]
    if not selected:
        st.info("먼저 시뮬레이터에서 과목을 선택해주세요.")
        return

    st.markdown(f"### ✅ 선택한 과목 ({len(selected)}개)")
    for s in selected:
        st.markdown(f"- {s}")

    st.download_button(
        "📥 텍스트 파일로 다운로드",
        data="\n".join(selected),
        file_name=f"신선여고_{year}_선택과목.txt",
        mime="text/plain",
    )


# ─────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────
if page == "🏠 홈":
    page_home()
elif page == "🗺️ 핵심 이수 경로":
    page_core_path()
elif page == "📚 학년별 교과목 탐색":
    page_explore()
elif page == "🧮 시간표 시뮬레이터":
    page_simulator()
elif page == "🎯 진로계열별 권장 과목":
    page_career()
elif page == "📄 결과 출력":
    page_export()
