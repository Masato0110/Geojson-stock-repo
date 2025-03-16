import json
import os
import re
import glob

def remove_properties_from_geojson(geojson, keys_to_remove):
    """
    GeoJSON内の各フィーチャーから、指定されたプロパティを削除する
    """
    for feature in geojson.get('features', []):
        properties = feature.get('properties', {})
        for key in keys_to_remove:
            if key in properties:
                del properties[key]
    return geojson

def sanitize_filename(filename):
    """
    ファイル名に使えない文字を除去する
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def process_geojson_file(filepath, keys_to_remove, output_dir):
    """
    1つのGeoJSONファイルを読み込み、不要なプロパティを削除して出力ディレクトリに保存する
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
    except Exception as e:
        print(f"Failed to load {filepath}: {e}")
        return

    cleaned_geojson = remove_properties_from_geojson(geojson_data, keys_to_remove)
    filename = os.path.basename(filepath)
    safe_filename = sanitize_filename(filename)
    output_filepath = os.path.join(output_dir, safe_filename)
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_geojson, f, ensure_ascii=False, indent=2)
        print(f"Processed: {filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Failed to save {output_filepath}: {e}")

def main(input_folder, output_folder, keys_to_remove):
    """
    指定したフォルダ内のすべての.geojsonファイルに対して処理を実行
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # input_folder 内の全ての .geojson ファイルを取得
    geojson_files = glob.glob(os.path.join(input_folder, "*.geojson"))
    if not geojson_files:
        print("対象のGeoJSONファイルが見つかりません。")
        return

    for filepath in geojson_files:
        process_geojson_file(filepath, keys_to_remove, output_folder)

if __name__ == '__main__':
    # 入力フォルダと出力フォルダのパスを指定
    input_folder = "../"   # ここに入力フォルダのパスを指定
    output_folder = "../" # 出力先フォルダ
    # 削除したいプロパティ名のリスト
    keys_to_remove = ['ID', '市区町村C', '大字コード', '丁目コード', '小字コード', '予備コード', '座標値種別', '地図名', '測地系判別']
    
    main(input_folder, output_folder, keys_to_remove)
