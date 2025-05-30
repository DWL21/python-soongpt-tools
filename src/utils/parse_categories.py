import json
import os
from collections import defaultdict
import pandas as pd
def parse_category(category_str):
    """
    category 문자열을 파싱하여 전필, 전선, 기타로 분류
    전기는 전선으로 분류
    """
    if not category_str:
        return "기타"
    if category_str.startswith("전필"):
        return "전필"
    elif category_str.startswith("전선") or category_str.startswith("전기"):
        return "전선"
    else:
        return "기타"
def parse_2025_1_courses():
    """
    result/2025_1 폴더의 모든 JSON 파일을 읽어서 category별로 파싱
    """
    folder_path = "result/2025_1"
    if not os.path.exists(folder_path):
        print(f"❌ {folder_path} 폴더를 찾을 수 없습니다.")
        return
    results = {
        "전필": [],
        "전선": [],
        "기타": []
    }
    all_courses = []
    file_stats = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    courses = json.load(f)
                file_category_count = defaultdict(int)
                for course in courses:
                    original_category = course.get('category', '')
                    parsed_category = parse_category(original_category)
                    course_data = course.copy()
                    course_data['parsed_category'] = parsed_category
                    course_data['source_file'] = filename
                    results[parsed_category].append(course_data)
                    all_courses.append(course_data)
                    file_category_count[parsed_category] += 1
                file_stats[filename] = dict(file_category_count)
                print(f"✓ 처리 완료: {filename} ({len(courses)}개 과목)")
            except Exception as e:
                print(f"✗ 오류 발생: {filename} - {e}")
    return results, all_courses, file_stats
def save_results(results, all_courses, file_stats):
    """
    결과를 다양한 형태로 저장
    """
    output_dir = "result/2025_1"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 디렉토리 생성: {output_dir}")
    for category, courses in results.items():
        output_file = os.path.join(output_dir, f"parsed_{category}_courses.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(courses, f, ensure_ascii=False, indent=2)
        print(f"저장 완료: {output_file} ({len(courses)}개 과목)")
    if all_courses:
        df = pd.DataFrame(all_courses)
        csv_file = os.path.join(output_dir, 'all_courses_with_parsed_category.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"저장 완료: {csv_file} ({len(all_courses)}개 과목)")
    create_statistics_report(results, file_stats, output_dir)
def create_statistics_report(results, file_stats, output_dir):
    """
    통계 보고서 생성
    """
    print("\n" + "="*60)
    print("📊 카테고리별 과목 통계")
    print("="*60)
    total_courses = sum(len(courses) for courses in results.values())
    for category, courses in results.items():
        count = len(courses)
        percentage = (count / total_courses * 100) if total_courses > 0 else 0
        print(f"{category}: {count:,}개 과목 ({percentage:.1f}%)")
    print(f"\n총 과목 수: {total_courses:,}개")
    print("\n" + "="*60)
    print("📁 파일별 카테고리 분포")
    print("="*60)
    for filename, stats in file_stats.items():
        print(f"\n[{filename}]")
        for category in ["전필", "전선", "기타"]:
            count = stats.get(category, 0)
            print(f"  {category}: {count}개")
    summary_stats = {
        "total_courses": total_courses,
        "category_distribution": {category: len(courses) for category, courses in results.items()},
        "file_statistics": file_stats
    }
    stats_file = os.path.join(output_dir, 'parsing_statistics.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(summary_stats, f, ensure_ascii=False, indent=2)
    print(f"\n저장 완료: {stats_file}")
def main():
    """
    메인 실행 함수
    """
    print("🚀 result/2025_1 폴더 과목 카테고리 파싱 시작...")
    if not os.path.exists("result/2025_1"):
        print("❌ result/2025_1 폴더를 찾을 수 없습니다.")
        return
    try:
        results, all_courses, file_stats = parse_2025_1_courses()
        save_results(results, all_courses, file_stats)
        print("\n✅ 파싱 완료!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
if __name__ == "__main__":
    main()
