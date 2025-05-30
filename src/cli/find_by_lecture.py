# -*- coding: utf-8 -*-

import json
import os
import argparse
import re
from typing import List, Dict, Optional
import subprocess
from dataclasses import dataclass
from ..core.schedule_parser import ScheduleParser, CourseTime

class CourseSearcher:
    def __init__(self):
        self.available_years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
        self.available_semesters = [1, 2]
        self.schedule_parser = ScheduleParser()

    def add_course_times(self, courses: List[Dict]) -> List[Dict]:
        """Add courseTime field to each course using schedule parser and remove schedule_room"""
        for course in courses:
            code = course.get('code', '')
            schedule_room = course.get('schedule_room', '')
            
            try:
                course_code = int(code) if code else 0
            except (ValueError, TypeError):
                course_code = 0
            
            # Parse schedule and create courseTime entries
            course_times = self.schedule_parser.parse_schedule_entry(schedule_room, course_code)
            
            # Convert CourseTime objects to dictionaries
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
            
            # Remove the original schedule_room field
            if 'schedule_room' in course:
                del course['schedule_room']
        
        return courses

    def search_by_keyword_local(self, year: int, semester: int, keyword: str, 
                               output_file: Optional[str] = None, grade: Optional[str] = None) -> List[Dict]:
        """
        로컬 JSON 파일들에서 키워드로 과목 검색
        """
        folder_path = os.path.join("result", f"{year}_{semester}")
        os.makedirs(folder_path, exist_ok=True)
        
        # --- search_<단어>.json 바로 반환 로직 추가 ---
        search_file = f"search_{keyword.replace(' ', '_')}.json"
        search_file_path = os.path.join(folder_path, search_file)
        if os.path.exists(search_file_path):
            print(f"🔎 '{keyword}'와 일치하는 search 파일 발견: {search_file}")
            with open(search_file_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
                if grade and grade != 'all':
                    results = self.filter_by_grade(results, grade)
                return results
        if not os.path.exists(folder_path):
            print(f"❌ 폴더 '{folder_path}'를 찾을 수 없습니다.")
            print(f"먼저 전공별 데이터를 수집해주세요.")
            return []
        
        matching_courses = []
        
        print(f"🔍 '{keyword}' 키워드로 과목 검색 중...")
        
        # 폴더 내 모든 JSON 파일 처리 (검색 결과 파일 제외)
        json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and not f.startswith('search_')]
        
        if not json_files:
            print(f"❌ '{folder_path}' 폴더에 전공별 JSON 파일이 없습니다.")
            return []
        
        for filename in json_files:
            file_path = os.path.join(folder_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    courses = json.load(f)
                
                # 키워드 검색
                for course in courses:
                    course_name = course.get('name', '').lower()
                    course_professor = course.get('professor', '').lower()
                    course_department = course.get('department', '').lower()
                    if (
                        keyword.lower() in course_name or
                        keyword.lower() in course_professor or
                        keyword.lower() in course_department
                    ):
                        matching_courses.append(course)
            
            except Exception as e:
                print(f"⚠️ 파일 읽기 오류: {filename} - {e}")
        
        # Add courseTime to all matching courses
        matching_courses = self.add_course_times(matching_courses)
        
        # 학년 필터 적용
        if grade and grade != 'all':
            matching_courses = self.filter_by_grade(matching_courses, grade)
        
        print(f"✅ 검색 완료: {len(matching_courses)}개 과목 발견")
        
        # 결과 저장 (result/year_semester 디렉토리 내부에 저장)
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

    def search_with_auto_fallback(self, year: int, semester: int, keyword: str, output_file: Optional[str] = None, force_cli: bool = False, grade: Optional[str] = None) -> List[Dict]:
        """
        로컬 검색 시도 후 결과가 없으면 자동으로 CLI 호출
        """
        folder_path = os.path.join("result", f"{year}_{semester}")
        
        # 강제 CLI 모드가 아닌 경우 로컬 검색 먼저 시도
        if not force_cli:
            # 폴더가 존재하고 JSON 파일이 있는지 확인
            if os.path.exists(folder_path):
                json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and not f.startswith('search_')]
                
                if json_files:
                    print("💾 로컬 JSON 파일에서 검색 중...")
                    results = self.search_by_keyword_local(year, semester, keyword, output_file, grade)
                    
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
                    # Add courseTime to CLI search results and remove schedule_room
                    results = self.add_course_times(results)
                    # 학년 필터 적용
                    if grade and grade != 'all':
                        results = self.filter_by_grade(results, grade)
                    # Save updated results with courseTime
                    with open(expected_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    print(f"📁 결과 저장: {expected_file}")
                    self.print_search_summary(results, keyword)
                    return results
                except Exception as e:
                    print(f"⚠️ CLI 결과 파일 읽기 오류: {e}")
            else:
                print("⚠️ CLI 실행은 성공했으나 결과 파일을 찾을 수 없습니다.")
        return []

    def filter_by_grade(self, courses: List[Dict], grade: str) -> List[Dict]:
        """
        target에 '1학년', '2학년' 등 학년이 포함된 과목만 반환
        grade는 '1'~'5' 또는 'all' 허용
        단, target에 '전체'가 포함되어 있으면 무조건 포함
        """
        grade_str = f"{grade}학년"
        filtered = []
        for course in courses:
            target = course.get('target', '')
            if '전체' in target:
                filtered.append(course)
            elif re.search(rf'\b{grade}학년\b', target):
                filtered.append(course)
        return filtered

    def print_search_summary(self, courses: List[Dict], keyword: str):
        """
        검색 결과 요약 출력
        """
        print(f"\n" + "="*60)
        print(f"📊 '{keyword}' 검색 결과 요약")
        print("="*60)
        
        if not courses:
            print("검색 결과가 없습니다.")
            return
        
        # 카테고리별 분류
        category_counts = {}
        department_counts = {}
        
        for course in courses:
            category = course.get('category', '기타')
            department = course.get('department', '미분류')
            
            category_counts[category] = category_counts.get(category, 0) + 1
            department_counts[department] = department_counts.get(department, 0) + 1
        
        print(f"총 과목 수: {len(courses)}개\n")
        
        # 카테고리별 통계
        print("📋 카테고리별 분포:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}개")
        
        print("\n🏛️ 학과별 분포:")
        for department, count in sorted(department_counts.items()):
            print(f"  {department}: {count}개")
        
        print("\n📚 과목 목록:")
        for i, course in enumerate(courses[:10], 1):  # 상위 10개만 표시
            name = course.get('name', '과목명 없음')
            professor = course.get('professor', '교수명 없음')
            department = course.get('department', '학과 없음')
            course_times = course.get('courseTime', [])
            
            print(f"  {i:2d}. {name} (교수: {professor}, 학과: {department})")
            
            # Display course time information
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
        description='숭실대학교 과목 검색 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python find_by_lecture.py 2025 1 "대학글쓰기"
  python find_by_lecture.py 2025 1 "프로그래밍" --cli
  python find_by_lecture.py 2025 1 "수학" --output math_courses.json
        """
    )
    
    parser.add_argument('year', type=int, help='연도 (예: 2025)')
    parser.add_argument('semester', type=int, choices=[1, 2], help='학기 (1 또는 2)')
    parser.add_argument('keyword', type=str, help='검색할 키워드')
    parser.add_argument('--cli', action='store_true', 
                       help='rusaint-cli 명령어 강제 사용 (기본값: 로컬 검색 후 필요시 CLI 자동 호출)')
    parser.add_argument('--output', '-o', type=str, 
                       help='결과 저장 파일명 (선택사항)')
    parser.add_argument('--grade', type=str, default='all', help='검색할 학년 (1~5, all=전체, 예: --grade 1)')
    
    args = parser.parse_args()
    
    searcher = CourseSearcher()
    
    print(f"🎓 숭실대학교 과목 검색 도구")
    print(f"📅 검색 조건: {args.year}년 {args.semester}학기")
    print(f"🔍 검색 키워드: '{args.keyword}'\n")
    
    # 언더스코어를 공백으로 변환
    search_keyword = args.keyword.replace('_', ' ')

    # 파라미터 검증
    if not searcher.validate_parameters(args.year, args.semester):
        return
    
    # 검색 실행 (자동 fallback 로직 사용)
    results = searcher.search_with_auto_fallback(
        args.year, args.semester, search_keyword, args.output, force_cli=args.cli, grade=args.grade
    )

    # 결과를 항상 기존 파일에 덮어쓰기
    if results:
        if args.output:
            output_path = args.output
        else:
            # 파일명 생성: search_{키워드}_{학년}.json 또는 search_{키워드}_전체.json
            keyword_part = search_keyword.replace(' ', '_')
            if args.grade and args.grade != 'all':
                filename = f"search_{keyword_part}_{args.grade}.json"
            else:
                filename = f"search_{keyword_part}_전체.json"
            
            output_path = os.path.join(
                "result", f"{args.year}_{args.semester}",
                filename
            )
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 최종 결과 저장: {output_path}")

    if args.cli or (results is None):
        return
    if not results:
        print(f"\n💡 '{search_keyword}' 키워드와 일치하는 과목을 찾을 수 없습니다.")
        print("다른 키워드로 시도해보거나, 전공별 데이터를 수집해주세요.")
        return


if __name__ == "__main__":
    main() 