import pandas as pd
import os

file_names = [
    "Y06_안전비상벨_TM.add",
    "Y14_경찰청_전국 지구대 파출소 주소 현황_20241231_TM.add",
    "Y14_경찰청_전국 치안센터 주소 현황_20250630_TM.add",
]

raw_dir = "data/raw"
out_dir = "data/raw"

# 시도할 구분자 후보
delimiters = [",", "|", "\t"]

for name in file_names:
    input_path = os.path.join(raw_dir, name)
    output_path = os.path.join(out_dir, name.replace(".add", ".csv"))
    success = False

    for enc in ["utf-8-sig", "cp949"]:
        for delim in delimiters:
            try:
                df = pd.read_csv(input_path, encoding=enc, delimiter=delim)
                df.to_csv(output_path, index=False, encoding="utf-8-sig")
                print(f"✅ 변환 완료: {output_path} (encoding={enc}, delimiter='{delim}')")
                success = True
                break
            except Exception:
                continue
        if success:
            break

    if not success:
        print(f"❌ 변환 실패: {name} — 인코딩/구분자 자동 탐지 실패")
