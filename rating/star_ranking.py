import json
import re

import pandas as pd

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def escape_single_quotes(value):
    """ 작은따옴표를 이스케이프 처리하는 함수 """
    if isinstance(value, str):
        return value.replace("'", "''")
    return value

def create_insert_query(table_name, data):
    queries = []
    for entry in data:
        columns = ', '.join(entry.keys())
        values = ', '.join(f"'{escape_single_quotes(value)}'" if isinstance(value, str) else str(value) for value in entry.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        queries.append(query)
    return queries

def create_sql():
    sorted_ranking = load_json_file('sorted_ranking.json')

    table_name = 'rating'
    insert_queries = create_insert_query(table_name, sorted_ranking)

    # SQL 파일로 저장
    with open('rating.sql', 'w', encoding='utf-8') as file:
        for query in insert_queries:
            file.write(query + '\n')

def rank():
    star_df = pd.read_json('star.json')

    star_df['star'] = star_df['star'].fillna(3)
    star_df['star'] = star_df['star'].replace(0, 3)

    sorted_df = star_df.sort_values(by='star', ascending=False).reset_index(drop=True)

    sorted_df['point'] = round(100 - sorted_df['star'].rank(method='min', ascending=False) / len(sorted_df) * 100, 2)

    sorted_df['course'] = sorted_df['course'].apply(lambda x: re.sub(r'\s*\([^)]*\)', '', str(x)) if str(x).endswith(')') else x)
    sorted_df = sorted_df.drop_duplicates(subset=['course', 'professor'])

    result_df = sorted_df[['course', 'professor', 'star', 'point']].rename(columns={'course': 'course_name', 'professor': 'professor_name'})

    result_df.to_json('sorted_ranking.json', orient='records', force_ascii=False, indent=4)

# 메인 실행 부분
if __name__ == "__main__":
    rank()
    create_sql()
    print("SQL 쿼리가 rating.sql 파일에 저장되었습니다.")
