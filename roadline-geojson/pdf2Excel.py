import pdfplumber
import pandas as pd

pdf_path = "【○深川出張所　道路台帳図（R6.3修正版）】/道路台帳図/1047深川雨竜線/10471404(R5).pdf"

with pdfplumber.open(pdf_path) as pdf:
    all_tables = []
    for page in pdf.pages:
        # 表をページごとに取得
        tables = page.extract_tables()
        for table in tables:
            all_tables.extend(table)

# 表データをDataFrameに変換
df = pd.DataFrame(all_tables)

# Excelに出力
excel_output_path = "座標データ.xlsx"
df.to_excel(excel_output_path, index=False, header=False)
