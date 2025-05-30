import json

from departments import li
import sorting


def run(first, index):
    now = count + index + 1
    if first in sorting.direct_changed:
        departments_value = sorting.direct(first)
    else:
        cleaned = sorting.clean(first)
        value = sorting.separate_department_grade(cleaned)
        changed_sorted_value =  sorting.to_set(sorting.change_to_sorted_key(value))
        departments_value = sorting.change_seperated(changed_sorted_value)
    results.append({
        "now": now,
        "first": first,
        "departments": departments_value
    })


count = 0
results = []
for index, first in enumerate(li[count:]):
    now = count + index + 1
    run(first, index)


# JSON 파일로 저장
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)



