import geopandas as gpd
import pandas as pd

# それぞれの GeoJSON ファイルを読み込み
gdf_nambu = gpd.read_file("釧路総合振興局.geojson")
gdf_hokubu = gpd.read_file("十勝総合振興局.geojson")

# 両レイヤーの座標参照系 (CRS) が同じであることを確認（異なる場合は統一する必要があります）
if gdf_nambu.crs != gdf_hokubu.crs:
    print("CRSが異なるので、統一します。")
    gdf_hokubu = gdf_hokubu.to_crs(gdf_nambu.crs)

# GeoDataFrame を結合（行方向に連結）
merged_gdf = pd.concat([gdf_nambu, gdf_hokubu], ignore_index=True)
merged_gdf = gpd.GeoDataFrame(merged_gdf, crs=gdf_nambu.crs)

# 結合した結果を GeoJSON として保存
output_file = "釧路・十勝総合振興局.geojson"
merged_gdf.to_file(output_file, driver="GeoJSON")
print(f"GeoJSON ファイル '{output_file}' に結合結果を保存しました。")
