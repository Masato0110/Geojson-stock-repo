import json
import requests
import os
import re

def sanitize_filename(filename):
    """
    ファイル名として使えない文字（\, /, *, ?, :, ", <, >, |）を取り除く
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_geojson_files(json_path, output_dir):
    # 保存先ディレクトリがなければ作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # JSONファイルを読み込む
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    for idx, (municipality, url) in enumerate(data.items(), start=1):
        print(f"Downloading ({idx}/{total}): {municipality}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
            safe_name = sanitize_filename(municipality)
            # 拡張子は .geojson として保存
            filename = f"{safe_name}.geojson"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as out_file:
                out_file.write(response.content)
            print(f"Saved: {filepath}")
        except Exception as e:
            print(f"Failed to download {municipality}: {e}")

if __name__ == "__main__":
    json_path = "hokkaido_municipalities_geojson.json"  # JSON ファイルのパス（必要に応じて変更）
    output_dir = "downloaded_geojson"  # ダウンロード先ディレクトリ名
    download_geojson_files(json_path, output_dir)
