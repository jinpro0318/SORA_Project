import requests
import pandas as pd
from pathlib import Path

# 1. 본인 발급받은 인증키 입력
API_KEY = "474a6e69566a696e3633464841694e"

# 2. URL 설정 (json으로 받는 게 가장 편함)
START_INDEX = 1
END_INDEX = 1000   # 한 번에 가져올 데이터 개수 (최대치 확인해서 조정 가능)
SERVICE = "safeOpenCCTV"

url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/{SERVICE}/{START_INDEX}/{END_INDEX}/"
print("🔗 요청 URL:", url)
# 3. API 요청 보내기
response = requests.get(url)
print("📡 상태 코드:", response.status_code)
print("📄 응답 내용:", response.text)

if response.status_code != 200:
    raise Exception(f"API 요청 실패: {response.status_code}")

# 4. JSON 응답 → DataFrame 변환
data = response.json()[SERVICE]["row"]
df = pd.DataFrame(data)

# 5. CSV 파일로 저장 (data/raw 폴더)
BASE_DIR = Path(__file__).resolve().parents[2]
output_file = BASE_DIR / "data" / "raw" / "Y05_서울시_안심이_CCTV_연계_현황.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"✅ 데이터 저장 완료: {output_file}")
print("📡 API 응답 상태 코드:", response.status_code)
print("📄 API 응답 내용:", response.text[:500])
print("📁 저장 경로:", output_file)