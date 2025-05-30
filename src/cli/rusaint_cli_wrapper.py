import json
import os
import argparse
import subprocess
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from ..core.schedule_parser import ScheduleParser, CourseTime
from src.core.ssu_data import SSU_DATA
class RusaintCLIWrapper:
    def __init__(self):
        """
        rusaint-cli 명령어들을 통합하여 관리하는 래퍼 클래스
        """
        self.schedule_parser = ScheduleParser()
        self.ssu_data = SSU_DATA
    def find_college_by_department(self, department: str) -> Optional[str]:
        """학부/학과명으로 단과대학 찾기"""
        for college in self.ssu_data['colleges']:
            if department in college['departments']:
                return college['name']
        return None
    def add_course_times(self, courses: List[Dict]) -> List[Dict]:
        """Add courseTime field to each course using schedule parser and remove schedule_room"""
        for course in courses:
            code = course.get('code', '')
            schedule_room = course.get('schedule_room', '')
            try:
                course_code = int(code) if code else 0
            except (ValueError, TypeError):
                course_code = 0
            course_times = self.schedule_parser.parse_schedule_entry(schedule_room, course_code)
            course['courseTime'] = [
                {
                    'week': ct.week,
                    'startTime': ct.startTime,
                    'endTime': ct.endTime,
                    'classroom': ct.classroom,
                    'courseCode': ct.courseCode
                }
                for ct in course_times
            ]
            if 'schedule_room' in course:
                del course['schedule_room']
        return courses
    def search_by_keyword_local(self, year: int, semester: int, keyword: str,
                               output_file: Optional[str] = None) -> List[Dict]:
        """
        로컬 JSON 파일들에서 키워드로 과목 검색
        """
        folder_path = os.path.join("result", f"{year}_{semester}")
        os.makedirs(folder_path, exist_ok=True)
        if not os.path.exists(folder_path):
            print(f"❌ 폴더 '{folder_path}'를 찾을 수 없습니다.")
            print(f"먼저 전공별 데이터를 수집해주세요.")
            return []
        matching_courses = []
        print(f"🔍 '{keyword}' 키워드로 과목 검색 중...")
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and not f.startswith('search_')]
        if not json_files:
            print(f"❌ '{folder_path}' 폴더에 전공별 JSON 파일이 없습니다.")
            return []
        for filename in json_files:
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    courses = json.load(f)
                for course in courses:
                    course_name = course.get('name', '').lower()
                    if keyword.lower() in course_name:
                        matching_courses.append(course)
            except Exception as e:
                print(f"⚠️ 파일 읽기 오류: {filename} - {e}")
        matching_courses = self.add_course_times(matching_courses)
        print(f"✅ 검색 완료: {len(matching_courses)}개 과목 발견")
        if matching_courses:
            if not output_file:
                output_file = f"search_{keyword.replace(' ', '_')}.json"
            output_path = os.path.join(folder_path, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(matching_courses, f, ensure_ascii=False, indent=2)
            print(f"📁 결과 저장: {output_path}")
            self.print_search_summary(matching_courses, keyword)
        return matching_courses
    def search_by_keyword_cli(self, year: int, semester: int, keyword: str) -> bool:
        """
        rusaint-cli find-by-lecture 명령어 실행
        """
        try:
            folder_path = os.path.join("result", f"{year}_{semester}")
            os.makedirs(folder_path, exist_ok=True)
            cmd = [
                'rusaint-cli', 'find-by-lecture',
                '--year', str(year),
                '--semester', str(semester),
                '--keyword', keyword
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=folder_path
            )
            if result.returncode == 0:
                print(f"✅ rusaint-cli 명령어 실행 완료")
                return True
            else:
                print(f"❌ rusaint-cli 명령어 실행 실패: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 명령어 실행 오류: {e}")
            return False
        except FileNotFoundError:
            print("❌ rusaint-cli 명령어를 찾을 수 없습니다.")
            return False
    def search_with_auto_fallback(self, year: int, semester: int, keyword: str,
                                 output_file: Optional[str] = None, force_cli: bool = False) -> List[Dict]:
        """
        로컬 검색 시도 후 결과가 없으면 자동으로 CLI 호출
        """
        folder_path = os.path.join("result", f"{year}_{semester}")
        if not force_cli:
            if os.path.exists(folder_path):
                json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and not f.startswith('search_')]
                if json_files:
                    print("💾 로컬 JSON 파일에서 검색 중...")
                    results = self.search_by_keyword_local(year, semester, keyword, output_file)
                    if results:
                        return results
                    else:
                        print(f"\n💡 로컬에서 '{keyword}' 키워드와 일치하는 과목을 찾을 수 없습니다.")
                        print("🌐 rusaint-cli를 통해 실시간 검색을 시도합니다...\n")
                else:
                    print(f"💡 '{folder_path}' 폴더에 전공별 데이터가 없습니다.")
                    print("🌐 rusaint-cli를 통해 실시간 검색을 시도합니다...\n")
            else:
                print(f"💡 '{folder_path}' 폴더가 존재하지 않습니다.")
                print("🌐 rusaint-cli를 통해 실시간 검색을 시도합니다...\n")
        print("🌐 rusaint-cli 명령어로 검색 중...")
        success = self.search_by_keyword_cli(year, semester, keyword)
        if success:
            expected_file = os.path.join(folder_path, f"search_{keyword.replace(' ', '_')}.json")
            if os.path.exists(expected_file):
                try:
                    with open(expected_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    results = self.add_course_times(results)
                    with open(expected_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print(f"✅ CLI 검색 결과를 로드했습니다: {len(results)}개 과목")
                    self.print_search_summary(results, keyword)
                    return results
                except Exception as e:
                    print(f"⚠️ CLI 결과 파일 읽기 오류: {e}")
            else:
                print("⚠️ CLI 실행은 성공했으나 결과 파일을 찾을 수 없습니다.")
        return []
    def get_major_info(self, year: int, semester: int, college: str,
                      department: str, major: Optional[str] = None) -> bool:
        """rusaint-cli를 사용하여 전공 정보 가져오기"""
        output_dir = os.path.join("result", f"{year}_{semester}")
        os.makedirs(output_dir, exist_ok=True)
        cmd = [
            'rusaint-cli', 'find-major',
            '--year', str(year),
            '--semester', str(semester),
            '--college', college,
            '--department', department
        ]
        if major:
            cmd.extend(['--major', major])
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=output_dir
            )
            if result.returncode == 0:
                print(f"✅ {year}_{semester}_{college}_{department} 완료")
                return True
            else:
                print(f"❌ 명령어 실행 실패: {result.stderr}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"❌ 명령어 실행 실패: {e}")
            return False
    def print_search_summary(self, courses: List[Dict], keyword: str):
        """
        검색 결과 요약 출력
        """
        print(f"\n" + "="*60)
        print(f"�� '{keyword}' 검색 결과 요약")
        print("="*60)
        if not courses:
            print("검색 결과가 없습니다.")
            return
        category_counts = {}
        department_counts = {}
        for course in courses:
            category = course.get('category', '기타')
            department = course.get('department', '미분류')
            category_counts[category] = category_counts.get(category, 0) + 1
            department_counts[department] = department_counts.get(department, 0) + 1
        print(f"총 과목 수: {len(courses)}개\n")
        print("📋 카테고리별 분포:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}개")
        print("\n🏛️ 학과별 분포:")
        for department, count in sorted(department_counts.items()):
            print(f"  {department}: {count}개")
        print("\n📚 과목 목록:")
        for i, course in enumerate(courses[:10], 1):
            name = course.get('name', '과목명 없음')
            professor = course.get('professor', '교수명 없음')
            department = course.get('department', '학과 없음')
            course_times = course.get('courseTime', [])
            print(f"  {i:2d}. {name} (교수: {professor}, 학과: {department})")
            if course_times:
                times_str = []
                for ct in course_times:
                    classroom_info = f" ({ct['classroom']})" if ct['classroom'] else ""
                    times_str.append(f"{ct['week']} {ct['startTime']}-{ct['endTime']}{classroom_info}")
                if times_str:
                    print(f"      ⏰ 시간: {', '.join(times_str)}")
            else:
                print(f"      ⏰ 시간: 정보 없음")
        if len(courses) > 10:
            print(f"  ... 외 {len(courses) - 10}개 과목")
    def validate_parameters(self, year: int, semester: int) -> bool:
        """
        입력 파라미터 검증
        """
        if year < 2020 or year > 2030:
            print(f"❌ 잘못된 연도: {year} (2020-2030 범위)")
            return False
        if semester not in [1, 2]:
            print(f"❌ 잘못된 학기: {semester} (1 또는 2만 가능)")
            return False
        return True
def main():
    parser = argparse.ArgumentParser(
        description='숭실대학교 rusaint-cli 통합 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
과목 검색:
  python rusaint_cli_wrapper.py find-by-lecture 2025 1 --keyword "대학글쓰기"
  python rusaint_cli_wrapper.py find-by-lecture 2025 1 --keyword "프로그래밍" --cli
  python rusaint_cli_wrapper.py find-by-lecture 2025 1 --keyword "수학" --output math_courses.json
전공별 과목 조회:
  python rusaint_cli_wrapper.py find-major 2025 1 --college "IT대학" --department "컴퓨터학부"
  python rusaint_cli_wrapper.py find-major 2025 1 --college "공과대학" --department "건축학부" --major "건축공학전공"
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='사용할 명령어')
    lecture_parser = subparsers.add_parser('find-by-lecture', help='과목 검색')
    lecture_parser.add_argument('year', type=int, help='연도 (예: 2025)')
    lecture_parser.add_argument('semester', type=int, choices=[1, 2], help='학기 (1 또는 2)')
    lecture_parser.add_argument('--keyword', required=True, help='검색할 키워드')
    lecture_parser.add_argument('--cli', action='store_true',
                               help='rusaint-cli 명령어 강제 사용 (기본값: 로컬 검색 후 필요시 CLI 자동 호출)')
    lecture_parser.add_argument('--output', '-o', type=str,
                               help='결과 저장 파일명 (선택사항)')
    major_parser = subparsers.add_parser('find-major', help='전공별 과목 조회')
    major_parser.add_argument('year', type=int, help='연도 (예: 2025)')
    major_parser.add_argument('semester', type=int, choices=[1, 2], help='학기 (1 또는 2)')
    major_parser.add_argument('--college', required=True, help='단과대학명')
    major_parser.add_argument('--department', required=True, help='학부/학과명')
    major_parser.add_argument('--major', help='세부 전공명 (선택사항)')
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    wrapper = RusaintCLIWrapper()
    print(f"🎓 숭실대학교 rusaint-cli 통합 도구")
    print(f"📅 검색 조건: {args.year}년 {args.semester}학기")
    if not wrapper.validate_parameters(args.year, args.semester):
        return
    if args.command == 'find-by-lecture':
        print(f"🔍 과목 검색 모드 - 키워드: '{args.keyword}'\n")
        results = wrapper.search_with_auto_fallback(
            args.year, args.semester, args.keyword, args.output, force_cli=args.cli
        )
        if not results:
            print(f"\n💡 '{args.keyword}' 키워드와 일치하는 과목을 찾을 수 없습니다.")
            print("다른 키워드로 시도해보거나, 전공별 데이터를 수집해주세요.")
    elif args.command == 'find-major':
        print(f"🏛️ 전공별 과목 조회 모드 - {args.college} {args.department}")
        if args.major:
            print(f"   세부 전공: {args.major}")
        print()
        success = wrapper.get_major_info(
            args.year, args.semester, args.college, args.department, args.major
        )
        if success:
            print("✅ 전공별 과목 조회가 완료되었습니다.")
        else:
            print("❌ 전공별 과목 조회에 실패했습니다.")
if __name__ == "__main__":
    main()
