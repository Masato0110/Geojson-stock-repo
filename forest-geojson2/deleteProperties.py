import os
import glob
import geopandas as gpd

def remove_properties_from_geojson(input_file, output_file, properties_to_remove=None, rename_map=None):
    """
    指定したGeoJSONファイルを読み込み、
    1. 不要なプロパティを削除し
    2. プロパティ名をリネームし
    3. 結果を別のファイルに保存する
    の処理を行います。
    """
    try:
        gdf = gpd.read_file(input_file)
    except Exception as e:
        print(f"Failed to read {input_file}: {e}")
        return

    # 不要なプロパティを削除
    if properties_to_remove:
        for prop in properties_to_remove:
            if prop in gdf.columns:
                gdf.drop(columns=prop, inplace=True)

    # プロパティ名をリネーム
    if rename_map:
        gdf.rename(columns=rename_map, inplace=True)

    try:
        gdf.to_file(output_file, driver="GeoJSON")
        print(f"Saved: {output_file}")
    except Exception as e:
        print(f"Failed to save {output_file}: {e}")

def process_all_geojson_in_folder(input_folder, output_folder, properties_to_remove=None, rename_map=None):
    """
    input_folder 内のすべての .geojson ファイルに対して処理を行い、
    output_folder に結果を保存します。
    """
    # 出力フォルダがなければ作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 指定フォルダ内のすべての .geojson ファイルを取得
    pattern = os.path.join(input_folder, "*.geojson")
    files = glob.glob(pattern)
    if not files:
        print("対象のGeoJSONファイルが見つかりませんでした。")
        return

    for input_file in files:
        basename = os.path.basename(input_file)
        # 出力ファイル名は、例えば "processed_" をプレフィックスに追加
        output_file = os.path.join(output_folder, basename)
        remove_properties_from_geojson(input_file, output_file, properties_to_remove, rename_map)

if __name__ == "__main__":
    # 処理対象のフォルダ（例）
    input_folder = "../forest-data2"  # 入力ファイルが入っているフォルダのパス
    output_folder = "../forest-data2"  # 出力先フォルダのパス

    # 削除したいプロパティのリスト
    properties_to_remove = [
        '支庁コード', '林班_y', '小班_y', '旧市町村', "管理区",
        '計画区コー', 'TEXT', 'UPDATEDATE', 'ALABELFLG', "EDITFACTOR",
        "LBLFLG", "SYOLBL", "GISAREA", "RIREKI", "NO", "LUX", "LUY",
        "ID", "RINSYO_ID2", "振興局_y", "市町村", "ＲＩＮＳＹＯＩＤ"
    ]
    # リネームしたいプロパティの対応表（旧名→新名）
    rename_map = {
        "市町村コー": '管理区',
        "市町村2": "市町村",
        "振興局_x": "振興局",
        "林班_x": "林班",
        "小班_x": "小班",
    }

    process_all_geojson_in_folder(input_folder, output_folder, properties_to_remove, rename_map)
