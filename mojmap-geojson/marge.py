import os
import glob
import json

def merge_geojson_files(input_folder, output_file):
    """
    指定したフォルダ内のすべての GeoJSON ファイルを読み込み、1つの FeatureCollection にまとめます。

    Parameters:
        input_folder (str): 入力フォルダのパス
        output_file (str): 出力ファイル（結合後の GeoJSON）のパス
    """
    # 入力フォルダ内の *.geojson ファイル一覧を取得
    geojson_files = glob.glob(os.path.join(input_folder, "*.geojson"))
    
    # 全ファイルの feature を格納するリスト
    merged_features = []
    
    # 各ファイルを読み込み、features を追加していく
    for file_path in geojson_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # GeoJSON が FeatureCollection の場合
                if data.get("type") == "FeatureCollection":
                    features = data.get("features", [])
                    merged_features.extend(features)
                # 単一の Feature の場合
                elif data.get("type") == "Feature":
                    merged_features.append(data)
                else:
                    print(f"警告: {file_path} はFeatureまたはFeatureCollectionではありません。スキップします。")
        except Exception as e:
            print(f"エラー: {file_path} の読み込みに失敗しました。エラー内容: {e}")
    
    # 結合後の GeoJSON オブジェクト（FeatureCollection）
    merged_geojson = {
        "type": "FeatureCollection",
        "features": merged_features
    }
    
    # 出力ファイルに書き込み
    try:
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(merged_geojson, out_f, ensure_ascii=False, indent=2)
        print(f"結合完了: {output_file} に書き込みました。")
    except Exception as e:
        print(f"エラー: 出力ファイル {output_file} の書き込みに失敗しました。エラー内容: {e}")

if __name__ == "__main__":
    # 入力フォルダと出力ファイル名を指定
    input_folder = "/Users/masato/Library/CloudStorage/OneDrive-筑波大学/GitHub/mojmap-geojson"  # ← GeoJSON ファイルが入っているフォルダのパスに変更してください
    output_file = "merged.geojson"               # ← 出力ファイル名（任意のパスに変更可能）
    
    merge_geojson_files(input_folder, output_file)
