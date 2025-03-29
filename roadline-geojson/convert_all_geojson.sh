#!/bin/bash
# フォルダ内の全ての .geojson を .topojson に変換
cd ../
source venv/bin/activate
cd roadline-geojson

for file in *.xlsm; do
    output="${file%.xlsm}.geojson"
    echo "Converting $file to $output"
    python3 excel2geojson.py "$file" "$output"
done

for file in *.geojson; do
    output="${file%.geojson}.topojson"
    geo2topo -q 1e6 "$file" > "$output"
done

for file in *.geojson; do
    rm "$file"
done

for file in *.topojson; do
    mv "$file" "/Users/masato/Desktop/法務省地図等検索ツール/public/test"
done

echo "All files converted successfully!"
deactivate
