import json
import sys
import os

def split_geojson_by_property(input_file, property_name="A45_014"):
    # 入力ファイルを読み込み
    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)
    
    # FeatureCollection であることを確認し、features を取得
    features = data.get("features", [])
    groups = {}

    # 各 Feature を property_name ごとにグループ化
    for feature in features:
        props = feature.get("properties", {})
        municipality = props.get(property_name)
        if not municipality:
            # プロパティが存在しない場合は "unknown" とするか、スキップ
            municipality = "unknown"
        groups.setdefault(municipality, []).append(feature)

    # 各グループごとに新たな GeoJSON ファイルとして出力
    for municipality, feats in groups.items():
        output_data = {
            "type": "FeatureCollection",
            "features": feats
        }
        # 出力ファイル名として municipality + ".geojson" を生成
        # ファイル名として使えない文字（例: "/"）が含まれていないか注意
        safe_name = municipality.replace("/", "_")
        output_file = f"{safe_name}.geojson"
        with open(output_file, "w", encoding="utf-8") as out_f:
            json.dump(output_data, out_f, ensure_ascii=False, indent=2)
        print(f"{output_file} に {len(feats)} 件のデータを書き込みました。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python split_geojson.py input.geojson")
        sys.exit(1)
    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"指定されたファイル '{input_file}' が存在しません。")
        sys.exit(1)
    split_geojson_by_property(input_file)
