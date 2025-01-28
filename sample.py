import json
from collections import defaultdict

# 元のGeoJSONファイルのパスを指定
input_geojson_path = "kokuyurinData.geojson"
output_directory = "output_geojson_files"

# 必要であれば出力ディレクトリを作成
import os
os.makedirs(output_directory, exist_ok=True)

# GeoJSONファイルを読み込む
def load_geojson(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 市町村ごとにデータを分割する
def split_geojson_by_property(data, property_key):
    city_data = defaultdict(list)

    for feature in data.get("features", []):
        city_name = feature["properties"].get(property_key)
        if city_name:
            city_data[city_name].append(feature)

    return city_data

# 分割したデータをGeoJSONとして保存
def save_geojson_files(city_data, output_dir):
    for city, features in city_data.items():
        output_path = os.path.join(output_dir, f"{city}.geojson")
        geojson_content = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_content, f, ensure_ascii=False, indent=2)

# メイン処理
def main():
    # GeoJSONファイルを読み込み
    geojson_data = load_geojson(input_geojson_path)

    # 市町村ごとに分割
    city_data = split_geojson_by_property(geojson_data, "A45_014")

    # 分割したデータを保存
    save_geojson_files(city_data, output_directory)
    print(f"市町村ごとに分割されたGeoJSONファイルが '{output_directory}' に保存されました。")

if __name__ == "__main__":
    main()
