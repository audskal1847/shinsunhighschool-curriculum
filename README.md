# 신선여자고등학교 고교학점제 이수 가이드북

학생들의 과목 선택을 돕는 Streamlit 기반 인터랙티브 웹앱입니다.

## 🚀 실행 방법
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 폴더 구조
```
duru_app/
├── app.py                              # 메인 앱
├── requirements.txt
├── README.md
└── data/
    ├── curriculum_2025.json            # 2025학년도 입학생 편제표 데이터
    ├── curriculum_2026.json            # 2026학년도 입학생 편제표 데이터
    ├── career_recommendations.json     # 진로계열별 권장 과목
    └── teacher_comments.json           # 과목별 담당교사 코멘트 (학교에서 채워 사용)
```

## ✨ 주요 기능
1. **🏠 홈**: 입학년도 선택 (2025/2026)
2. **🗺️ 핵심 이수 경로**: 졸업까지 필요한 영역별 학점 안내
3. **📚 학년별 교과목 탐색**: 학년/학기별 과목 카드 보기
4. **🧮 시간표 시뮬레이터** ⭐: 학생이 직접 과목을 체크 → 학점·필수요건 자동 검증
5. **🎓 2028 대입 권장 과목**: 진로계열별 추천 과목
6. **🖨️ 결과 출력**: 상담용 HTML/CSV 다운로드 (PDF는 브라우저 인쇄 활용)

## 🛠 데이터 수정
- 편제표 변경 시 `data/curriculum_*.json` 파일을 직접 수정하거나, 엑셀에서 재변환
- 과목별 교사 코멘트는 `data/teacher_comments.json`에 추가:
```json
{
  "2025": {
    "공통국어1": {
      "comment": "기초 문해력을 다지는 과목입니다.",
      "prerequisite": ""
    }
  }
}
```
