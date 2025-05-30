import subprocess
import os
import argparse
from typing import Dict, List, Optional
from src.core.ssu_data import SSU_DATA
from ..core.schedule_parser import ScheduleParser, CourseTime
from src.cli.rusaint_cli_wrapper import RusaintCLIWrapper
from src.utils.department_matcher import department_matcher
import json
import re
class SSUMajorFinder:
    def __init__(self):
        self.ssu_data = SSU_DATA
        self.wrapper = RusaintCLIWrapper()
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
    def filter_by_department(self, courses: List[Dict], departments: List[str]) -> List[Dict]:
        """
        target에 지정된 학과/학부 중 하나가 포함된 과목만 반환 (줄임말 지원)
        """
        filtered = []
        for course in courses:
            target = course.get('target', '')
            if not target:
                continue
            if '전체' in target:
                filtered.append(course)
                continue
            if department_matcher.matches_any_department(target, departments):
                filtered.append(course)
        return filtered
    def find_college_by_department(self, department: str) -> Optional[str]:
        """학부/학과명으로 단과대학 찾기"""
        for college in self.ssu_data['colleges']:
            if department in college['departments']:
                return college['name']
        return None
    def get_major_info(self, year: int, semester: int, college: str,
                      department: str, major: Optional[str] = None, subdepartments: Optional[List[str]] = None, grade: Optional[str] = None) -> dict:
        output_dir = os.path.join("result", f"{year}_{semester}")
        os.makedirs(output_dir, exist_ok=True)
        possible_base_files = [
            f"{year}_{semester}학기_{college}_{department}_전공.json",
            f"{college}_{department}_{major}.json" if major else f"{college}_{department}.json"
        ]
        if subdepartments:
            for subdept in subdepartments:
                possible_base_files.insert(0, f"{year}_{semester}학기_{college}_{department}_{subdept}_전공.json")
        base_path = None
        for possible_file in possible_base_files:
            potential_path = os.path.join(output_dir, possible_file)
            if os.path.exists(potential_path):
                base_path = potential_path
                break
        college_part = college.replace(' ', '')
        department_part = department.replace(' ', '')
        subdept_part = ""
        if subdepartments:
            subdept_cleaned = [subdept.replace(' ', '') for subdept in subdepartments]
            subdept_part = "&" + "&".join(subdept_cleaned)
        if grade and grade != 'all':
            output_file = f"major_{college_part}_{department_part}{subdept_part}_{grade}.json"
        else:
            output_file = f"major_{college_part}_{department_part}{subdept_part}_전체.json"
        output_path = os.path.join(output_dir, output_file)
        if os.path.exists(output_path):
            print(f"✅ 로컬 파일 사용: {output_path}")
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        if base_path:
            print(f"✅ 원본 파일 사용: {base_path}")
            with open(base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            wrapper = RusaintCLIWrapper()
            data = wrapper.add_course_times(data)
            if subdepartments:
                all_departments = [department] + subdepartments
                data = self.filter_by_department(data, all_departments)
                print(f"✅ 부전공 필터 적용: {', '.join(all_departments)}")
            if grade and grade != 'all':
                data = self.filter_by_grade(data, grade)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과 저장: {output_path}")
            return data
        print(f"🌐 로컬 파일 없음, rusaint_cli_wrapper로 수집")
        self.wrapper.get_major_info(year, semester, college, department, major)
        for possible_file in possible_base_files:
            potential_path = os.path.join(output_dir, possible_file)
            if os.path.exists(potential_path):
                base_path = potential_path
                break
        if base_path:
            with open(base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            wrapper = RusaintCLIWrapper()
            data = wrapper.add_course_times(data)
            if subdepartments:
                all_departments = [department] + subdepartments
                data = self.filter_by_department(data, all_departments)
                print(f"✅ 부전공 필터 적용: {', '.join(all_departments)}")
            if grade and grade != 'all':
                data = self.filter_by_grade(data, grade)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과 저장: {output_path}")
            return data
        else:
            print(f"❌ rusaint-cli 실행 후에도 파일을 찾을 수 없습니다")
            print(f"   확인된 파일들: {[f for f in os.listdir(output_dir) if f.endswith('.json')]}")
            return {}
    def get_all_majors_info(self, year: int, semester: int,
                           output_dir: str = 'result', grade: Optional[str] = None):
        """모든 학부/학과의 전공 정보 가져오기"""
        for college in self.ssu_data['colleges']:
            college_name = college['name']
            print(f"\n=== {college_name} 처리 중 ===")
            for department in college['departments']:
                print(f"  - {department} 조회 중...")
                if ' ' in department and any(keyword in department for keyword in ['전공', '학부']):
                    parts = department.split(' ')
                    if len(parts) >= 2:
                        dept_name = parts[0]
                        major_name = ' '.join(parts[1:])
                        self.get_major_info(year, semester, college_name, dept_name, major_name, subdepartments=None, grade=grade)
                    else:
                        self.get_major_info(year, semester, college_name, department, subdepartments=None, grade=grade)
                else:
                    self.get_major_info(year, semester, college_name, department, subdepartments=None, grade=grade)
def main():
    parser = argparse.ArgumentParser(description='숭실대학교 전공 정보 수집 스크립트')
    parser.add_argument('year', type=int, help='연도 (예: 2025)')
    parser.add_argument('semester', type=int, choices=[1, 2], help='학기 (1 또는 2)')
    parser.add_argument('--department', '-d', action='append', help='학과/학부명 (여러 번 사용 가능, 첫 번째는 주전공, 나머지는 부전공)')
    parser.add_argument('--grade', type=str, default='all', help='검색할 학년 (1~5, all=전체, 예: --grade 1)')
    args = parser.parse_args()
    finder = SSUMajorFinder()
    print(f"=== 숭실대학교 전공 정보 수집 스크립트 ({args.year}년 {args.semester}학기) ===\n")
    if args.department:
        college = finder.find_college_by_department(args.department[0])
        if college:
            print(f"단과대학: {college}")
            print(f"학과/학부: {args.department[0]}")
            if args.department[1:]:
                print(f"부전공: {', '.join(args.department[1:])}")
            if ' ' in args.department[0] and any(keyword in args.department[0] for keyword in ['전공', '학부']):
                parts = args.department[0].split(' ')
                if len(parts) >= 2:
                    dept_name = parts[0]
                    major_name = ' '.join(parts[1:])
                    finder.get_major_info(args.year, args.semester, college, dept_name, major_name, args.department[1:] if len(args.department) > 1 else None, args.grade)
                else:
                    finder.get_major_info(args.year, args.semester, college, args.department[0], subdepartments=args.department[1:] if len(args.department) > 1 else None, grade=args.grade)
            else:
                finder.get_major_info(args.year, args.semester, college, args.department[0], subdepartments=args.department[1:] if len(args.department) > 1 else None, grade=args.grade)
        else:
            print(f"오류: '{args.department[0]}' 학과/학부를 찾을 수 없습니다.")
            print("사용 가능한 학과/학부 목록:")
            for college in finder.ssu_data['colleges']:
                print(f"\n[{college['name']}]")
                for dept in college['departments']:
                    print(f"  - {dept}")
    else:
        finder.get_all_majors_info(args.year, args.semester, grade=args.grade)
if __name__ == "__main__":
    main()
