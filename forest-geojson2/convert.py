import os
import glob
import geopandas as gpd
import pandas as pd

def read_single_sheet_excel(xlsx_path):
    # Excelファイルを開く
    with pd.ExcelFile(xlsx_path) as xls:
        # シート名のリストを取得
        sheet_names = xls.sheet_names
        if len(sheet_names) == 0:
            raise ValueError(f"'{xlsx_path}'にシートがありません。")
        elif len(sheet_names) > 1:
            print(f"警告: '{xlsx_path}' には複数のシートがありますが、先頭のシートのみ読み込みます。")
        
        # 先頭のシート名を取得
        first_sheet = sheet_names[0]
        # そのシートをDataFrameとして読み込み
        df = pd.read_excel(xls, sheet_name=first_sheet)
        return df

def process_folder(folder_path):
    """
    指定したフォルダ内にあるシェープファイル（.shp）と Excel（.xlsx）を探し出し、
    KEYCODE でマージして GeoJSON を出力する関数。
    """
    # フォルダ内の *.shp と *.xlsx を検索
    shp_files = glob.glob(os.path.join(folder_path, "*.shp"))
    xlsx_files = glob.glob(os.path.join(folder_path, "*.xlsx"))

    if not shp_files or not xlsx_files:
        print(f"SKIP: {folder_path} にシェープファイルまたは Excelファイルが見つかりません。")
        return

    # （単純化のため、最初に見つかったファイルを使用する）
    shp_path = shp_files[0]
    xlsx_path = xlsx_files[0]

    print(f"Processing folder: {folder_path}")
    print(f"  Shapefile: {os.path.basename(shp_path)}")
    print(f"  Excel: {os.path.basename(xlsx_path)}")

    # GeoJSON 出力ファイル名を決定（シェープファイル名をベースに .geojson にする例）
    shp_basename = os.path.splitext(os.path.basename(shp_path))[0]  # 例: "991000_ss"
    output_geojson = os.path.join('', f"{shp_basename}.geojson")

    # シェープファイルを読み込み
    gdf = gpd.read_file(shp_path)
    df = read_single_sheet_excel(xlsx_path)

    # KEYCODE 列の型を統一（文字列化）
    gdf["KEYCODE"] = gdf["KEYCODE"].astype(str)
    df["KEYCODE"] = df["KEYCODE"].astype(str)

    # 左結合でマージ
    merged_gdf = gdf.merge(df, on="KEYCODE", how="left")

    # GeoJSON として保存
    merged_gdf.to_file(output_geojson, driver="GeoJSON")
    print(f"  => 出力: {output_geojson}")
    print("Done.\n")

def main():
    # 処理対象のベースディレクトリ（フォルダ）を指定
    base_dir = "元データ"  # ★実際のパスに書き換えてください

    # base_dir 直下のサブフォルダを走査
    for entry in os.scandir(base_dir):
        if entry.is_dir():
            process_folder(entry.path)

if __name__ == "__main__":
    main()
