import requests
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

# 1. API 키
API_KEY = "42CE8QSA-42CE-42CE-42CE-42CE8QSASL"

# 2. 요청 파라미터 설정
params = {
    "serviceKey": API_KEY,
    "pageNo": "1",
    "numOfRows": "1000",  # 필요에 따라 조정
    "type": "xml"         # xml(기본값), json도 가능하지만 보통 xml이 안정적
}

url = "http://safemap.go.kr/openApiService/data/getCmmpoiEmgbellData.do"

# 3. 요청 보내기
response = requests.get(url, params=params)
print("📡 상태 코드:", response.status_code)
print("📄 응답 샘플:", response.text[:300])

if response.status_code != 200:
    raise Exception(f"❌ API 요청 실패: {response.status_code}")

# 4. XML 파싱
root = ET.fromstring(response.content)
rows = []

for item in root.findall(".//item"):
    row = {child.tag: child.text for child in item}
    rows.append(row)

if not rows:
    raise Exception("❌ 데이터가 비어 있음. API 키 또는 파라미터 확인 필요")

# 5. DataFrame 변환
df = pd.DataFrame(rows)

# 6. CSV 저장
BASE_DIR = Path(__file__).resolve().parents[2]
output_file = BASE_DIR / "data" / "raw" / "Y06_안전비상벨.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"✅ 저장 완료: {output_file}")
