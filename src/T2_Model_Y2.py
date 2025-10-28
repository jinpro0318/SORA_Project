"""
SORA (Seoul Risk Analytics for Women & Aged)
안전수치(리스크 인덱스) 산출 + 지도 시각화 스크립트 (Folium)

✅ 입력: X/Y 계열 CSV (지역구 단위)
✅ 처리: 파일 로드 → 최신연도 집계 → Min-Max 정규화 → X/Y 가중합 → RiskIndex 계산
✅ 시각화: 지역구별 안전지수 수평 바차트 + 지도 단계구분도(Choropleth)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import json
import warnings
warnings.filterwarnings('ignore')

# =============================
# 0) 파일 경로 설정
# =============================
X_FILES = {
    "X01_5대범죄": ("X01_5대범죄_발생검거_누적건수.csv", "지역구", "누적건수"),
    "X01_피해자": ("X01_범죄피해자_발생_연간건수_2020_2024.csv", "지역구", "연간발생건수"),
    "X02_112": ("X02_112신고출동_연간건수_2020_2024.csv", "지역구", "출동건수"),
    "X03_범죄발생": ("X03_범죄발생_건수_20231231기준.csv", "지역구", "발생건수"),
    "X07_성폭력": ("X07_성폭력위험요소_지수.csv", "지역구", "위험요소지수"),
    "X09_유흥": ("X09_유흥주점_수.csv", "지역구", "주점수"),
    "X13_여성노인": ("X13_여성독거노인_현황_2020_2024.csv", "지역구", "여성독거노인수"),
}

Y_FILES = {
    "Y06_CCTV": ("Y06_CCTV_설치수.csv", "지역구", "설치수"),
    "Y07_안심벨": ("Y07_안심벨_설치수.csv", "지역구", "설치수"),
    "Y14_지구대": ("Y14_지구대파출소_설치수_20241231기준.csv", "지역구", "설치수"),
    "Y14_치안센터": ("Y14_치안센터_설치수_20250630기준.csv", "지역구", "설치수"),
    "Y15_경찰관": ("Y15_경찰관_인원수_2020_2024.csv", "지역구", "인원수"),
}

# =============================
# 1) 가중치 설정
# =============================
WEIGHTS_X = {
    "X01_5대범죄": 0.10,
    "X01_피해자": 0.10,
    "X02_112": 0.25,
    "X03_범죄발생": 0.15,
    "X07_성폭력": 0.20,
    "X09_유흥": 0.10,
    "X13_여성노인": 0.10,
}

WEIGHTS_Y = {
    "Y06_CCTV": 0.30,
    "Y07_안심벨": 0.20,
    "Y14_지구대": 0.25,
    "Y14_치안센터": 0.15,
    "Y15_경찰관": 0.10,
}

# =============================
# 2) 정규화 함수
# =============================
def minmax(series: pd.Series):
    s = series.astype(float)
    mn, mx = s.min(), s.max()
    if mx == mn:
        return pd.Series(0.5, index=s.index)
    return (s - mn) / (mx - mn)

# =============================
# 3) 데이터 로드 및 병합
# =============================
def load_file(path, gu_col, val_col):
    df = pd.read_csv(path)
    df = df[[gu_col, val_col]].copy()
    df.columns = ["지역구", "값"]
    df = df.groupby("지역구", as_index=False)["값"].sum()
    return df

def build_matrix(file_dict, prefix):
    merged = None
    for key, (path, gu, val) in file_dict.items():
        df = load_file(path, gu, val)
        df.rename(columns={"값": f"{prefix}_{key}"}, inplace=True)
        if merged is None:
            merged = df
        else:
            merged = merged.merge(df, on="지역구", how="outer")
    return merged

# =============================
# 4) 리스크 지수 계산
# =============================
def compute_safety_index(X_df, Y_df):
    df = X_df.merge(Y_df, on="지역구", how="outer")
    for c in df.columns:
        if c != "지역구":
            df[c] = pd.to_numeric(df[c], errors='coerce')

    for c in [col for col in df.columns if col.startswith("X_")]:
        df[c+"_norm"] = minmax(df[c])
    for c in [col for col in df.columns if col.startswith("Y_")]:
        df[c+"_inv"] = 1 - minmax(df[c])

    df["Vulnerability"] = 0
    for key, w in WEIGHTS_X.items():
        col = f"X_{key}_norm"
        if col in df.columns:
            df["Vulnerability"] += df[col] * w

    df["Defense"] = 0
    for key, w in WEIGHTS_Y.items():
        col = f"Y_{key}_inv"
        if col in df.columns:
            df["Defense"] += df[col] * w

    df["RiskIndex"] = df["Vulnerability"] / (df["Vulnerability"] + df["Defense"])
    df["RiskIndex"] = df["RiskIndex"].fillna(0.5)
    df["RiskQuintile"] = pd.qcut(df["RiskIndex"], 5, labels=["매우낮음","낮음","보통","높음","매우높음"])

    return df

# =============================
# 5) 시각화 함수 (바차트)
# =============================
def visualize_risk(df):
    plot_df = df.sort_values("RiskIndex", ascending=True)
    plt.figure(figsize=(12,8))
    sns.barplot(data=plot_df, x="RiskIndex", y="지역구", palette="RdYlGn_r")
    plt.title("서울시 여성 및 노인 대상 범죄 위험도 (Risk Index)", fontsize=14)
    plt.xlabel("Risk Index (높을수록 위험)")
    plt.ylabel("지역구")

    for i, (idx, row) in enumerate(plot_df.iterrows()):
        plt.text(row.RiskIndex + 0.005, i, f"{row.RiskIndex:.2f}", va='center')

    plt.tight_layout()
    plt.show()

# =============================
# 6) 시각화 함수 (지도)
# =============================

def visualize_map(df, geo_path, value_col="RiskIndex"):
    with open(geo_path, encoding='utf-8') as f:
        geo_data = json.load(f)

    # Folium 지도 생성 (서울 중심 좌표)
    m = folium.Map(location=[37.5502, 126.982], zoom_start=11)

    folium.Choropleth(
        geo_data=geo_data,
        data=df,
        columns=["지역구", value_col],
        key_on='feature.id',
        fill_color='PuRd',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name='서울시 위험도 지수'
    ).add_to(m)

    return m

# =============================
# 7) 실행부
# =============================
if __name__ == "__main__":
    X_df = build_matrix(X_FILES, "X")
    Y_df = build_matrix(Y_FILES, "Y")
    result = compute_safety_index(X_df, Y_df)
    result.to_csv("SORA_Risk_Index_Result.csv", index=False, encoding="utf-8-sig")
    print("✅ 분석 완료: SORA_Risk_Index_Result.csv 저장")
    print(result.head())

    visualize_risk(result)

    # 지도 시각화 (json 파일 경로는 직접 지정)
    GEO_PATH = "./skorea_municipalities_geo_simple.json"
    m = visualize_map(result, GEO_PATH)
    m.save("SORA_Risk_Index_Map.html")
    print("✅ 지도 저장 완료: SORA_Risk_Index_Map.html")
