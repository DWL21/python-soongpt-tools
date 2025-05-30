import json
import os
from typing import Dict, Set, List
from src.core.ssu_data import SSU_DATA
class DepartmentMatcher:
    def __init__(self):
        self.official_departments = set()
        for college in SSU_DATA['colleges']:
            for dept in college['departments']:
                self.official_departments.add(dept)
        self.department_to_abbreviations = self._create_department_abbreviations()
    def _create_department_abbreviations(self) -> Dict[str, Set[str]]:
        """각 정식 학과명에 대한 가능한 줄임말들 매핑 생성"""
        mapping = {}
        base_mappings = {
            '소프트웨어학부': {'소프트', '소프트웨어학부', 'SW학부', '소프트웨어'},
            '국어국문학과': {'국문', '국어국문학과', '국어국문'},
            '영어영문학과': {'영문', '영어영문학과', '영어영문'},
            '독어독문학과': {'독문', '독어독문학과', '독어독문'},
            '불어불문학과': {'불문', '불어불문학과', '불어불문'},
            '중어중문학과': {'중문', '중어중문학과', '중어중문'},
            '일어일문학과': {'일문', '일어일문학과', '일어일문'},
            '컴퓨터학부': {'컴퓨터', '컴퓨터학부'},
            '글로벌미디어학부': {'글로벌미디어', '글로벌미디어학부'},
            '글로벌통상학과': {'글로벌통상', '글로벌통상학과'},
            '벤처중소기업학과': {'벤처중소', '벤처중소기업학과'},
            '회계학과': {'회계학과', '회계'},
            '경영학부': {'경영학부', '경영'},
            '금융학부': {'금융', '금융학부'},
            '법학과': {'법학', '법학과'},
            '국제법무학과': {'국제법무학과', '국제법무'},
            '기계공학부': {'기계', '기계공학부'},
            '전기공학부': {'전기', '전기공학부'},
            '화학공학과': {'화공', '화학공학과'},
            '신소재공학과': {'신소재', '신소재공학과'},
            '산업정보시스템공학과': {'산업정보', '산업정보시스템공학과'},
            '건축학부 건축학전공': {'건축학부', '건축학전공', '건축학'},
            '건축학부 건축공학전공': {'건축공학', '건축공학전공'},
            '건축학부 실내건축전공': {'실내건축', '실내건축전공'},
            '물리학과': {'물리', '물리학과'},
            '수학과': {'수학', '수학과'},
            '화학과': {'화학', '화학과'},
            '정보통계보험수리학과': {'통계보험', '정보통계보험수리학과'},
            '의생명시스템학부': {'의생명시스템', '의생명', '의생명시스템학부'},
            '사회복지학부': {'사회복지', '사회복지학부'},
            '언론홍보학과': {'언론홍보', '언론홍보학과'},
            '정보사회학과': {'정보사회', '정보사회학과'},
            '정치외교학과': {'정외', '정치외교학과'},
            '평생교육학과': {'평생교육', '평생교육학과'},
            '행정학부': {'행정학부', '행정'},
            '기독교학과': {'기독교', '기독교학과'},
            '철학과': {'철학', '철학과'},
            '사학과': {'사학', '사학과'},
            '스포츠학부': {'스포츠', '스포츠학부'},
            '예술창작학부 문예창작전공': {'문예창작전공', '문예창작'},
            '예술창작학부 영화예술전공': {'영화예술전공', '영화예술'},
            'AI융합학부': {'AI융합학부', 'AI융합'},
            '전자정보공학부 전자공학전공': {'전자공학전공', '전자공학'},
            '전자정보공학부 IT융합전공': {'IT융합전공', 'IT융합'},
            '정보보호학과': {'정보보호학과', '정보보호'},
            '미디어경영학과': {'미디어경영', '미디어경영학과'},
            '경제학과': {'경제', '경제학과'},
            '자유전공학부': {'자유전공학부', '자유전공'},
            '차세대반도체학과': {'차세대반도체학과', '차세대반도체'},
        }
        for official_name, abbreviations in base_mappings.items():
            if official_name in self.official_departments:
                mapping[official_name] = abbreviations.copy()
        try:
            self._extract_from_classification_files(mapping)
        except Exception as e:
            print(f"Warning: Could not load classification files: {e}")
        return mapping
    def _extract_from_classification_files(self, mapping: Dict[str, Set[str]]):
        """수강분류 파일들에서 추가 줄임말 추출"""
        classification_files = [
            'classification/수강분류_가공_전 (3).json',
            'classification/수강분류_가공_후 (3).json'
        ]
        for file_path in classification_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    for item in data:
                        if not item or item == "":
                            continue
                        self._extract_abbreviations_from_text(item, mapping)
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")
    def _extract_abbreviations_from_text(self, text: str, mapping: Dict[str, Set[str]]):
        """텍스트에서 줄임말을 추출하여 매핑에 추가"""
        parts = text.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        for part in parts:
            if any(exclude in part for exclude in ['학년', '전체', '제한', '수강', '가능', '불가', '대상외', '순수외국인']):
                continue
            for official_name in self.official_departments:
                if part in official_name and len(part) >= 2:
                    if official_name not in mapping:
                        mapping[official_name] = {official_name}
                    mapping[official_name].add(part)
    def matches_department(self, target_text: str, department: str) -> bool:
        """target 텍스트가 주어진 학과와 매칭되는지 확인 (줄임말 지원)"""
        if not target_text or not department:
            return False
        if department in target_text:
            return True
        if department in self.department_to_abbreviations:
            abbreviations = self.department_to_abbreviations[department]
            for abbrev in abbreviations:
                if abbrev in target_text:
                    return True
        return False
    def matches_any_department(self, target_text: str, departments: List[str]) -> bool:
        """target 텍스트가 주어진 학과들 중 하나와 매칭되는지 확인"""
        for dept in departments:
            if self.matches_department(target_text, dept):
                return True
        return False
department_matcher = DepartmentMatcher()
