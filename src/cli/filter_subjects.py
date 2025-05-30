import ijson
import json
import glob
import os
import argparse
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))
from ssu_data import SSU_DATA

# 사전 로딩
def load_abbr_map():
    with open('classification/수강분류_가공_전 (3).json', encoding='utf-8') as f:
        raw_keys = json.load(f)
    with open('classification/수강분류_가공_후 (3).json', encoding='utf-8') as f:
        mapped_keys = json.load(f)
    return {k: v for k, v in zip(raw_keys, mapped_keys)}

INCLUDE_ALL = ['전체', '전체학년', '전체학년 전체']
EXCLUDE_KEYWORDS = ['외국인', '순수외국인', '유학생']

def get_college_departments(college_name):
    for college in SSU_DATA['colleges']:
        if college['name'] == college_name:
            return set(college['departments'])
    return set()

def is_include(target):
    if any(word in target for word in INCLUDE_ALL):
        return True
    if any(word in target for word in EXCLUDE_KEYWORDS):
        return False
    return target in abbr_map

def get_mapped_target(target):
    if any(word in target for word in INCLUDE_ALL):
        return '전체'
    return abbr_map.get(target, target)

def find_college_by_department(department):
    for college in SSU_DATA['colleges']:
        if department in college['departments']:
            return college['name']
    return None

def get_college_departments_by_department(department):
    college_name = find_college_by_department(department)
    if college_name:
        return get_college_departments(college_name)
    return set()

def match_department_or_college(target, department):
    # 표준화된 target에서 학과 또는 소속 단과대의 학과 포함 여부
    if department and department in target:
        return True
    college_departments = get_college_departments_by_department(department)
    for dept in college_departments:
        if dept in target:
            return True
    return False

def filter_by_department_year(input_path, output_path, department, year):
    abbr_map = load_abbr_map()
    filtered = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for item in ijson.items(f, 'item'):
            target = item.get('target', '')
            item_year = str(item.get('year', ''))
            mapped_target = get_mapped_target(target)
            # 전체는 무조건 포함
            if '전체' in mapped_target:
                filtered.append(item)
                continue
            # 전체학년이 target에 있으면 학년 무시, 학과/단과대만 체크
            if '전체학년' in mapped_target or '전체학년 전체' in mapped_target:
                if match_department_or_college(mapped_target, department):
                    filtered.append(item)
                continue
            # year 일치 + 학과/단과대 일치
            if item_year == str(year) and match_department_or_college(mapped_target, department):
                filtered.append(item)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    print(f'Filtered by department/year result saved to {output_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='수강분류 사전 기반 필터링 및 표준화')
    parser.add_argument('--department', type=str, help='학과명')
    parser.add_argument('--year', type=int, help='연도')
    parser.add_argument('--mode', type=str, default='abbr', choices=['abbr', 'department'], help='필터 모드: abbr(기본), department(학과/단과대/연도)')
    args = parser.parse_args()

    abbr_map = load_abbr_map()
    input_files = glob.glob('result/2025_1/2025_1학기_*.json')
    if not input_files:
        print('No input files found.')
        exit(1)
    input_path = input_files[0]
    if args.mode == 'abbr':
        output_path = os.path.join(os.path.dirname(input_path), 'search_filtered_2025_1학기.json')
        filtered = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for item in ijson.items(f, 'item'):
                target = item.get('target', '')
                if is_include(target):
                    item['target'] = get_mapped_target(target)
                    filtered.append(item)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        print(f'Filtered result saved to {output_path}')
    elif args.mode == 'department':
        if not args.department or not args.year:
            print('--department와 --year를 반드시 지정해야 합니다.')
            exit(1)
        output_path = os.path.join(os.path.dirname(input_path), f'search_{args.department}_{args.year}.json')
        filter_by_department_year(input_path, output_path, args.department, args.year) 