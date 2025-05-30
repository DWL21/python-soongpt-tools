import glob
import json

# 패턴에 맞는 모든 파일을 찾음
for filename in glob.glob('result/2025_1/2025_1학기_*.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def process(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "code" and isinstance(v, str):
                    prefix = "SALV_WD_TABLE.ID_DE0D9128A4327646C94670E2A892C99C:VIEW_TABLE.SE_SHORT_SALV_WD_CE."
                    if v.startswith(prefix):
                        obj[k] = v.replace(prefix, "")
                else:
                    process(v)
        elif isinstance(obj, list):
            for item in obj:
                process(item)

    process(data)

    # 덮어쓰기
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)