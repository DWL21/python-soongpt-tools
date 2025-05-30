# -*- coding: utf-8 -*-
import re
import sys
from turtledemo.lindenmayer import replace

from departments import li

sys.setrecursionlimit(3000)

transform_sorted = dict()
transform_sorted['IT대학'] = 'AI융합학부&글로벌미디어학부&미디어경영학과&소프트웨어학부&전자정보공학부 IT융합전공&전자정보공학부 전자공학전공&정보보호학과&컴퓨터학부'
transform_sorted['경영대학'] = '경영학부&금융학부&벤처경영학과&벤처중소기업학과&복지경영학과&혁신경영학과&회계세무학과&회계학과'
transform_sorted['경제통상대학'] = '경제학과&국제무역학과&글로벌통상학과&금융경제학과&통상산업학과'
transform_sorted['공과대학'] = '건축학부 건축공학전공&건축학부 건축학부&건축학부 건축학전공&건축학부 실내건축전공&기계공학부&산업정보시스템공학과&신소재공학과&전기공학부&화학공학과'
transform_sorted['법과대학'] = '국제법무학과&법학과'
transform_sorted['베어드학부대학'] = '자유전공학부'
transform_sorted['사회과학대학'] = '사회복지학부&언론홍보학과&정보사회학과&정치외교학과&평생교육학과&행정학부'
transform_sorted['인문대학'] = '국어국문학과&기독교학과&독어독문학과&불어불문학과&사학과&스포츠학부&영어영문학과&예술창작학부 문예창작전공&예술창작학부 영화예술전공&일어일문학과&중어중문학과&철학과'
transform_sorted['자연과학대학'] = '물리학과&수학과&의생명시스템학부&정보통계보험수리학과&화학과'
transform_sorted['전체'] = '차세대반도체학과&IT대학&경영대학&경제통상대학&공과대학&법과대학&베어드학부대학&사회과학대학&인문대학&자연과학대학'

transform = dict()
transform['경영학부'] = '경영학부'
transform['벤처중소'] = '벤처중소기업학과'
transform['화공'] = '화학과'
transform['IT융합전공'] = '전자정보공학부 IT융합전공'
transform['IT융합'] = '전자정보공학부 IT융합전공'
transform['회계학과'] = '회계학과'
transform['회계'] = '회계학과'
transform['기계'] = '기계공학부'
transform['통계보험'] = '정보통계보험수리학과'
transform['의생명시스템'] = '의생명시스템학부'
transform['AI융합학부'] = 'AI융합학부'
transform['신소재'] = '신소재공학과'
transform['전자공학전공'] = '전자정보공학부 전자공학전공'
transform['전기'] = '전기공학부'
transform['화학'] = '화학공학과'
transform['전체'] = '전체'
transform['글로벌미디어'] = '글로벌미디어학부'
transform['물리'] = '물리학과'
transform['컴퓨터'] = '컴퓨터학부'
transform['건축학부'] = '건축학부 건축공학전공&건축학부 건축학부&건축학부 건축학전공&건축학부 실내건축전공'
transform['산업정보'] = '산업정보시스템공학과'
transform['언론홍보'] = '언론홍보학과'
transform['소프트'] = '소프트웨어학부'
transform['행정학부'] = '행정학부'
transform['건축공학'] = '건축학부 건축공학전공'
transform['문예창작전공'] = '예술창작학부 문예창작전공'
transform['문예창작'] = '예술창작학부 문예창작전공'
transform['글로벌통상'] = '글로벌통상학과'
transform['일어일문'] = '일어일문학과'
transform['수학'] = '수학과'
transform['금융경제'] = '금융경제학과'
transform['금융'] = '금융학부'
transform['경제'] = '경제학과'
transform['정보사회'] = '정보사회학과'
transform['건축학'] = '건축학부 건축공학전공&건축학부 건축학부&건축학부 건축학전공&건축학부 실내건축전공'
transform['국제법무학과'] = '국제법무학과'
transform['법학'] = '법학과'
transform['중문'] = '중어중문학과'
transform['철학'] = '철학과'
transform['사학'] = '사학과'
transform['사회복지'] = '사회복지학부'
transform['정외'] = '정치외교학과'
transform['평생교육'] = '평생교육학과'
transform['영문'] = '영어영문학과'
transform['실내건축'] = '건축학부 실내건축전공'
transform['국문'] = '국어국문학과'
transform['독문'] = '독어독문학과'
transform['불문'] = '불어불문학과'
transform['영화예술전공'] = '예술창작학부 영화예술전공'
transform['영화예술'] = '예술창작학부 영화예술전공'
transform['기독교'] = '기독교학과'
transform['IT대'] = 'IT대학'
transform['경영대'] = '경영대학'
transform['자연대'] = '자연과학대학'
transform['공대'] = '공과대학'
transform['금융학부'] = '금융학부'
transform['AI융합'] = 'AI융합학부'
transform['자유전공학부'] = '자유전공학부'
transform['스포츠'] = '스포츠학부'
transform['미디어경영'] = '미디어경영학과'
transform['공과대'] = '공과대학'
transform['사회대'] = '사회과학대학'
transform['인문대'] = '인문대학'
transform['경통대'] = '경제통상대학'
transform['전자정보공학부-IT융합'] = '전자정보공학부 IT융합전공'
transform['전자정보공학부-전자공학'] = '전자정보공학부 전자공학전공'
transform['SW학부'] = '소프트웨어학부'
transform['글로벌미디어학부'] = '글로벌미디어학부'
transform['정보보호학과'] = '정보보호학과'
transform['법대'] = '법과대학'
transform['차세대반도체학과'] = '차세대반도체학과'
transform['전자정보'] = '전자정보공학부 IT융합전공&전자정보공학부 전자공학전공'
transform['컴퓨터학부'] = '컴퓨터학부'
transform['회계세무학과'] = '회계세무학과'
transform['이공계전체'] = '차세대반도체학과&IT대학&공과대학&자연과학대학'
transform['사과대'] = '사회과학대학'
transform['법과대'] = '법과대학'
transform['전자공학'] = '전자정보공학부 전자공학전공'
transform['차세대반도체'] = '차세대반도체학과'
transform['정보보호'] = '정보보호학과'
transform[
    '비철학과대상'] = '차세대반도체학과&IT대학&경영대학&경제통상대학&공과대학&법과대학&베어드학부대학&사회과학대학&자연과학대학&국어국문학과&기독교학과&독어독문학과&불어불문학과&사학과&스포츠학부&영어영문학과&예술창작학부 문예창작전공&예술창작학부 영화예술전공&일어일문학과&중어중문학과'
transform['순수외국인입학생제한'] = '전체'
transform[
    '스포츠제외'] = '차세대반도체학과&IT대학&경영대학&경제통상대학&공과대학&법과대학&베어드학부대학&사회과학대학&자연과학대학&국어국문학과&기독교학과&독어독문학과&불어불문학과&사학과&영어영문학과&예술창작학부 문예창작전공&예술창작학부 영화예술전공&일어일문학과&중어중문학과&철학과'
transform['산업정보시스템공학과'] = '산업정보시스템공학과'
transform['정통전'] = '정보통계보험수리학과'
transform['정보통계보험수리학과'] = '정보통계보험수리학과'
transform['의생명'] = '의생명시스템학부'
transform['벤처경영학과'] = '벤처경영학과'
transform['복지경영학과'] = '복지경영학과'
transform['인문사회자연계전체'] = '인문대학&사회과학대학&자연과학대학'
transform['혁신경영학과'] = '혁신경영학과'
transform['산업·정보'] = '산업정보시스템공학과'
transform['정치외교'] = '정치외교학과'


def change_seperated(value: str) -> str:
    result = []
    stack = value.rstrip('&').split('&')

    while stack:
        x = stack.pop()
        if x and x.endswith("!") and x[:-2] in transform_sorted:
            stack.extend(list(map(lambda y: f'{y}{x[-2]}!', transform_sorted[x[:-2]].split('&'))))
        elif x and x[:-1] in transform_sorted:
            stack.extend(list(map(lambda y: f'{y}{x[-1]}', transform_sorted[x[:-1]].split('&'))))
        else:
            result.append(x)
    return '&'.join(result)


def change_to_sorted_key(value: str) -> str:
    result = []
    for x in transform.keys():
        start_index = value.find(x)
        if x in value:
            grade = value[start_index + len(x)]
            if grade not in ["1", "2", "3", "4", "5", '*']:
                grade = ''
            if start_index + len(x) + 1 < len(value) and value[start_index + len(x) + 1] == '!':
                result.append(add_info_department(transform[x], grade, reverse=True))
            else:
                result.append(add_info_department(transform[x], grade))
        value = value.replace(x, '')
    return '&'.join(result)


direct_changed = dict()
direct_changed['2학년 \n3학년 \n4학년 \n5학년 (대상외수강제한)'] = '전체2&전체3&전체4&전체5'
direct_changed[
    "2학년 경영학부 ,회계학과 ,벤처중소 ,금융, 보험계리리스크\n3학년 경영학부 ,회계학과 ,벤처중소 ,금융, 보험계리리스크\n4학년 경영학부 ,회계학과 ,벤처중소 ,금융, 보험계리리스크"] \
    = '2경영학부&2회계학과&2벤처중소&2금융&3경영학부&3회계학과&3벤처중소&3금융&4경영학부&4회계학과&4벤처중소&4금융'
direct_changed["3학년 사학\n4학년 사학"] = '사학과3&사학과4'
direct_changed["3학년 전체\n4학년 전체"] = '전체3&전체4'
direct_changed["3학년 전체\n4학년 전체\n5학년 전체"] = '전체3&전체4&전체5'
direct_changed["3학년 컴퓨터\n4학년 컴퓨터"] = '컴퓨터학부3&컴퓨터학부4'
direct_changed[
    "3학년 컴퓨터학부, SW학부, AI융합학부, 글로벌미디어학부 ,IT융합전공\n4학년 컴퓨터학부, SW학부, AI융합학부, 글로벌미디어학부 ,IT융합전공\n5학년 컴퓨터학부, SW학부, AI융합학부, 글로벌미디어학부 ,IT융합전공 (대상외수강제한)"] \
    = '컴퓨터학부3&소프트웨어학부3&AI융합학부3&글로벌미디어학부3&전자정보공학부 IT융합전공3&컴퓨터학부4&소프트웨어학부4&AI융합학부4&글로벌미디어학부4&전자정보공학부 IT융합전공4&컴퓨터학부5&소프트웨어학부5&AI융합학부5&글로벌미디어학부5&전자정보공학부 IT융합전공5'
direct_changed["3학년 회계학과\n4학년 회계학과"] = "회계학과3&회계학과4"
direct_changed["4학년 전체\n5학년 전체 (대상외수강제한)"] = "전체4&전체5"
direct_changed["비철학과 대상"] = "전체*&철학과*!"
direct_changed["전체"] = "전체*"
direct_changed["전체(1학년 제외)"] = '전체*&전체1!'
direct_changed["전체(물리학과 제외)"] = '전체*&물리학과*!'
direct_changed["전체(철학과제외)"] = "전체*&철학과*!"
direct_changed["전체(화학과 제외)"] = "전체*&화학과*!"
direct_changed["전체학과(물리학과 제외)"] = "전체*&물리학과*!"
direct_changed["전체학년"] = "전체*"
direct_changed["전체학년 컴퓨터학부,빅데이터컴퓨팅융합"] = "컴퓨터학부*"
direct_changed["1학년 글로벌통상\n2학년 글로벌통상\n3학년 글로벌통상\n4학년 글로벌통상"] = "글로벌통상학과1&글로벌통상학과2&글로벌통상학과3&글로벌통상학과4"
direct_changed["1학년 내국인학생 전체 수강제한 \\/\\/ 전체학년 수강 신청일: 2학년 이상 전체 단과대학 학생(1학년 외국인유학생 포함) 수강신청 가능"] = "전체2&전체3&전체4&전체5"
direct_changed["3학년 의생명시스템, 빅데이터컴퓨팅융합, 지식재산융합(정보통계보험수리학과 전체학년 제외)"] = "의생명시스템학부3"
direct_changed["3학년 인문대, 자연대, 경영대 \\/\\/ 전체학년 수강 신청일: 2학년 이상 내국인 전체(1학년 외국인 포함) 수강신청 가능"] = "인문대학3&자연과학대학3&경영대학3"
direct_changed["4학년 금융경제(금융경제학과 및 경제학과만 수강 가능)"] = "금융경제학과4&경제학과4"
direct_changed["4학년 금융경제(금융경제학과 및 경제학과만 수강 가능) ,금융경제"] = "금융경제학과4&경제학과4"
direct_changed["전체학년 경영학부;시간제 (대상외수강제한)"] = "경영학부*"
direct_changed[
    "전체학년 인문사회자연계 전체(인문대,자연대,사회대,법대,경통대,경영대) 및 자유전공학부 (대상외수강제한)"] = "경제통상대학*&사회과학대학*&인문대학*&법과대학*&자연과학대학*&경영대학*&자유전공학부*"
direct_changed["1학년 IT대(전자공학,IT융합,AI융합) (대상외수강제한)"] = "AI융합학부1&전자정보공학부 IT융합전공1&전자정보공학부 전자공학전공1"
direct_changed["1학년 IT대(컴퓨터,글로벌미디어,소프트) (대상외수강제한)"] = "컴퓨터학부1&소프트웨어학부1&글로벌미디어학부1"


def direct(value: str) -> str:
    return direct_changed[value]


replacements = dict()
replacements['타학과 학생 수강 제한'] = ''
replacements[' '] = ''
replacements['(대상외수강제한)'] = ''
replacements['(타학과수강제한)'] = ''
replacements['(계약학과)'] = ''
replacements['및'] = ','
replacements['자유전공학부1'] = '자유전공학부'
replacements['자유전공학부2'] = '자유전공학부'
replacements['자유전공학부A'] = '자유전공학부'
replacements['자유전공학부B'] = '자유전공학부'
replacements['자유전공학부C'] = '자유전공학부'
replacements['자유전공학부D'] = '자유전공학부'
replacements['스포츠마케팅융합'] = ''
replacements['정보보호융합'] = ''
replacements['순환경제·친환경화학소재'] = ''
replacements['순환경제·친환경융합'] = ''
replacements['중국어경제통상'] = ''
replacements["IT융합전공 ,컴퓨터 ,소프트 ,AI융합학부 ,글로벌미디어 ,정보보호(계약), 교류학과"] = "IT융합전공 ,컴퓨터 ,소프트 ,AI융합학부 ,글로벌미디어 ,정보보호(계약), 교류학과"


def clean(item: str) -> str:
    for old, new in replacements.items():
        item = item.replace(old, new)
    item = item.split('/')[0].strip()
    if '외국인' in item:
        return ''
    if '교직이수자' in item:
        return ''
    return item


grades = dict()
grades['1학년'] = '1'
grades['2학년'] = '2'
grades['3학년'] = '3'
grades['4학년'] = '4'
grades['5학년'] = '5'
grades['1학년전체'] = '1'
grades['2학년전체'] = '2'
grades['3학년전체'] = '3'
grades['4학년전체'] = '4'
grades['5학년전체'] = '5'
grades['전체학년'] = '*'
grades['전체학과'] = '*'
grades['전체'] = '*'


def separate_department_grade(value: str) -> str:
    result = []
    matches = [re.sub(r'\(.*?\)', '', value)] + re.findall(r'\((.*?)\)', value)
    for match in matches:
        flag = False
        reverse = False
        if "수강제한" in match or "제외" in match or "제한" in match:
            match = match.replace("수강제한", "")
            match = match.replace("제한", "")
            match = match.replace("제외", "")
            reverse = True
        for key, grade in grades.items():
            if key in match:
                match = match.replace(key, '')
                extract(grade, match, result, reverse=reverse)
                flag = True
                continue
        if not flag:
            for key, grade in grades.items():
                if key in value:
                    extract(grade, match, result, reverse=reverse)
                    continue
            extract(grades['전체'], match, result, reverse=reverse)
    return '&'.join(result)


def extract(grade, match, result, reverse=False):
    exclusions = match.strip().split(',')
    if reverse:
        for exclusion in exclusions:
            result.append(f"{exclusion.strip()}{grade}!")
        return
    for exclusion in exclusions:
        result.append(f"{exclusion.strip()}{grade}")


def to_set(value: str) -> str:
    return '&'.join(list(set(value.split('&'))))


def add_info_department(value: str, grade, reverse=False) -> str:
    if reverse:
        return f"{value.replace('&', f'{grade}!&')}{grade}!"
    return f"{value.replace('&', f'{grade}&')}{grade}"
