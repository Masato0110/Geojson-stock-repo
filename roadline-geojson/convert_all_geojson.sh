#!/bin/bash
# フォルダ内の全ての .geojson を .topojson に変換
for file in *.xlsm; do
    output="${file%.xlsm}.geojson"
    echo "Converting $file to $output"
    python3 excel2geojson.py "$file" "$output"
done

for file in *.geojson; do
    output="${file%.geojson}.topojson"
    echo "Converting $file to $output"
    geo2topo -q 1e6 "$file" > "$output"
done

for file in *.geojson; do
    rm "$file"
done

echo "All files converted successfully!"
