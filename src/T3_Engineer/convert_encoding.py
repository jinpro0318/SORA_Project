import pandas as pd
import os

# 변환할 파일 목록
files = [
    "data/raw/X03_경찰청_범죄 발생 지역별 통계_20231231.csv",
    "data/raw/X09_서울시 유흥주점영업 인허가 정보.csv",
    "data/raw/Y08_가로등 위치 정보.csv",
    "data/raw/Y15_경찰청 서울특별시경찰청_경찰서별 경찰관 수 현황_20241231.csv",
    "data/raw/Y15_경찰청_전국 경찰서별 경찰관 현황_20231231.csv",
]

for file in files:
    try:
        df = pd.read_csv(file, encoding='cp949')
        # 덮어쓰기 대신 UTF-8 버전으로 따로 저장 (원본 보존)
        name, ext = os.path.splitext(file)
        new_file = f"{name}_utf8{ext}"
        df.to_csv(new_file, index=False, encoding='utf-8')
        print(f"✅ 변환 완료: {new_file}")
    except Exception as e:
        print(f"❌ 변환 실패: {file} — {e}")
