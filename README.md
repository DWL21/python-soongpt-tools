# 숭실대학교 rusaint-cli Python 도구 모음

## 📦 폴더 구조

```
src/
├── cli/
│   ├── rusaint_cli_wrapper.py      # 통합 CLI 엔트리포인트
│   ├── find_by_lecture.py          # 키워드 기반 과목 검색 CLI
│   └── get_major.py                # 전공별 과목 수집 CLI
├── core/
│   ├── schedule_parser.py          # 시간표 파서 및 데이터 모델
│   ├── category_parser.py          # 카테고리 파서
│   └── course_searcher.py          # 검색/파싱 핵심 로직 (공통)
├── utils/
│   └── parse_categories.py         # 카테고리 일괄 파싱 유틸
```

## 🛠️ 주요 기능 및 명령어

### 1. 과목 검색 (키워드 기반)
- 키워드로 과목 검색, 자동 fallback(로컬→CLI)
- 결과는 `{년도}_{학기}/search_{키워드}.json`에 저장

```bash
python -m src.cli.find_by_lecture 2025 1 "자료구조" --grade 1
```
- `--grade` 옵션 사용 시 해당 학년(target에 '1학년', '2학년' 등 포함)만 검색 결과에 포함
- 단, **target에 '전체'라는 단어가 포함된 과목은 학년 필터와 무관하게 항상 포함**
- 예시: `--grade 1`을 줘도 target에 '전체'가 있으면 그 과목은 결과에 포함됨

```bash
python -m src.cli.find_by_lecture 2025 1 "자료구조" --grade all
```
- 학년 필터 없이 전체 검색(기본값)

### 2. 전공별 과목 수집
- 단과대학/학부/전공별 rusaint-cli 실시간 데이터 수집

```bash
python -m src.cli.get_major 2025 1 --department "컴퓨터학부" --grade 1
```
- `--grade` 옵션 사용 시 해당 학년(target에 '1학년', '2학년' 등 포함)만 검색 결과에 포함
- **단, target에 '전체'라는 단어가 포함된 과목은 학년 필터와 무관하게 항상 포함**
- 예시: `--grade 1`을 줘도 target에 '전체'가 있으면 그 과목은 결과에 포함됨

```bash
python -m src.cli.get_major 2025 1 --department "컴퓨터학부" --grade all
```
- 학년 필터 없이 전체 검색(기본값)

```bash
python -m src.cli.get_major 2025 1 --department "컴퓨터학부" --department "소프트웨어학부" --grade 1
```
- 여러 학과 지정 시 사용 (첫 번째는 주전공, 나머지는 부전공)
- 파일명: `major_{단과대}_{학과}&{부전공1}&{부전공2}_{학년|전체}.json` 형태로 저장

```bash
python -m src.cli.get_major 2025 1 --department "컴퓨터학부" --department "소프트웨어학부" --department "전자정보공학부" --grade all
```
- 여러 부전공을 가진 경우 예시

### 3. 카테고리 일괄 파싱/통계
- `result/2025_1` 폴더의 모든 JSON 파일을 읽어서 전필/전선/기타 분류, 통계 및 CSV/JSON 저장
- 결과는 `result/2025_1/parsed_*.json` 및 `all_courses_with_parsed_category.csv`에 저장

```bash
python -m src.utils.parse_categories
```

**결과 파일들:**
- `result/2025_1/parsed_전필_courses.json` - 전공필수 과목들
- `result/2025_1/parsed_전선_courses.json` - 전공선택 과목들  
- `result/2025_1/parsed_기타_courses.json` - 기타 과목들
- `result/2025_1/all_courses_with_parsed_category.csv` - 전체 과목 CSV
- `result/2025_1/parsing_statistics.json` - 파싱 통계

### 4. 수강분류 필터링 및 표준화
- 줄임말 사전 기반 필터링 또는 학과/단과대/연도 기반 필터링 지원
- 결과는 `result/2025_1/search_*.json`에 저장

#### (1) 줄임말 사전 기반 필터링
```bash
python -m src.cli.filter_subjects
```
- 결과: `result/2025_1/search_filtered_2025_1학기.json`

#### (2) 학과/단과대/연도 기반 필터링
```bash
python -m src.cli.filter_subjects --mode department --department "컴퓨터학부" --year 2025
```
- `--department` : 필수, 학과명(예: "컴퓨터학부")
- `--year` : 필수, 연도(예: 2025)
- `--mode department` : 학과/단과대/연도 기반 필터링 모드
- 결과: `result/2025_1/search_{학과명}_{연도}.json` (예: `search_컴퓨터학부_2025.json`)

**필터링 로직:**
- 입력한 학과명에 해당하는 단과대 소속 모든 학과명도 자동으로 포함되어 매칭됩니다.
- target이 "전체"면 무조건 포함
- target에 "전체학년"이 포함되어 있으면 학년은 무시하고 학과/단과대만 체크
- target이 해당 학과명 또는 소속 단과대의 학과명과 일치하고, year도 일치하면 포함

## 🧩 모듈 설명

- **core/schedule_parser.py**: 시간표 문자열 파싱, CourseTime 데이터 모델
- **core/category_parser.py**: 카테고리 문자열 파싱(전필/전선/기타)
- **core/course_searcher.py**: 과목 검색/파싱 공통 로직(통합 예정)
- **cli/rusaint_cli_wrapper.py**: find-by-lecture, find-major 등 통합 CLI
- **cli/find_by_lecture.py**: 키워드 기반 과목 검색 CLI
- **cli/get_major.py**: 전공별 과목 수집 CLI
- **utils/parse_categories.py**: 전체 JSON 일괄 카테고리 파싱 및 통계

## 📂 데이터 구조 예시

```json
{
  "name": "자료구조",
  "professor": "심경민",
  "category": "전필-소프트",
  "courseTime": [
    { "week": "목", "startTime": "16:30", "endTime": "17:45", "classroom": "정보과학관 21203 (김재상강의실", "courseCode": 878 },
    { "week": "금", "startTime": "16:30", "endTime": "17:45", "classroom": "정보과학관 21203 (김재상강의실", "courseCode": 878 }
  ]
}
```

## ⚡ 설치 및 준비

- Python 3.7+
- (옵션) rusaint-cli 설치 및 PATH 등록
  - curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  - cargo install rusaint-cli
- (옵션) pandas 설치: `pip install pandas`
