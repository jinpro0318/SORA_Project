import pandas as pd

file_path = 'C:\Users\user\Desktop\0.data\SORA_Project-1\SORA_Project\data\raw\여성_대상_범죄_통계.csv' 

# 2. CSV 파일 읽기
try:
    df_crime = pd.read_csv(file_path, encoding='utf-8')
    
    # 데이터가 잘 불러와졌는지 확인하기 위해 상위 5개 행을 출력
    print("데이터 불러오기 성공!")
    print(df_crime.head())
    
except FileNotFoundError:
    print(f"오류: '{file_path}' 파일을 찾을 수 없습니다. 파일 경로와 이름을 다시 확인해주세요.")
except Exception as e:
    # 한글 인코딩 문제로 오류가 날 경우를 대비한 추가 처리
    print(f"다른 인코딩으로 재시도 중... 현재 오류: {e}")
    try:
        df_crime = pd.read_csv(file_path, encoding='cp949') # 윈도우 기본 인코딩
        print("데이터 불러오기 성공 (cp949)")
        print(df_crime.head())
    except:
        print("파일 불러오기에 실패했습니다. 파일이 깨졌거나 인코딩 문제가 심각합니다.")