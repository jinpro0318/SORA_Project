import os
import requests
import xmltodict
import pandas as pd
from datetime import datetime

# ✅ API 정보
API_KEY = "42CE8QSA-42CE-42CE-42CE-42CE8QSASL"
BASE_URL = "https://safemap.go.kr/openApiService/data/getCmmpoiEmgbellData.do"

# 📁 저장 경로
RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

FILE_PREFIX = "Y06_openapi_안전비상벨"

def fetch_page(page_no=1, num_of_rows=100):
    """
    page_no 기준으로 데이터 한 페이지 요청
    """
    params = {
        "serviceKey": API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return xmltodict.parse(resp.text)

def fetch_all():
    """
    전체 페이지를 돌며 모든 데이터를 수집
    깨진 페이지가 있어도 멈추지 않고 건너뜀
    """
    all_items = []
    page = 1

    while True:
        print(f"[FETCH] page {page}")
        try:
            data_dict = fetch_page(page)
        except Exception as e:
            print(f"[WARN] page {page} 오류 발생 → 건너뜀 ({e})")
            page += 1
            continue

        body = data_dict.get("response", {}).get("body", {})
        items = body.get("items", {}).get("item", [])

        # 데이터가 없으면 루프 종료
        if not items:
            print(f"[INFO] page {page} 이후 데이터 없음. 수집 종료.")
            break

        if isinstance(items, dict):
            items = [items]

        all_items.extend(items)
        page += 1

    print(f"[INFO] 총 수집 건수: {len(all_items)}")
    return all_items

def save_to_csv(items):
    """
    수집한 전체 데이터를 CSV로 저장
    """
    today = datetime.today().strftime("%Y%m%d")
    csv_filename = f"{FILE_PREFIX}_{today}.csv"
    csv_path = os.path.join(RAW_DIR, csv_filename)

    df = pd.DataFrame(items)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"[SAVE] CSV 파일 저장 완료: {csv_path}")

if __name__ == "__main__":
    all_items = fetch_all()
    save_to_csv(all_items)
