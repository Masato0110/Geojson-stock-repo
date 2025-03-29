import pandas as pd
import json
import numpy as np
import pandas as pd
import json
import sys
import argparse

def calc_lat_lon(x, y):
    """ 平面直角座標を緯度経度に変換する
    - input:
        (x, y): 変換したいx, y座標[m]
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
    - output:
        latitude:  緯度[度]
        longitude: 経度[度]
        * 小数点以下は分・秒ではないことに注意
    """
    # 平面直角座標系原点をラジアンに直す
    phi0_rad = np.deg2rad(44.00)
    lambda0_rad = np.deg2rad(142.25)
    
    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. ) 
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])
  
    def beta_array(n):
        b0 = np.nan # dummy
        b1 = (1./2)*n - (2./3)*(n**2) + (37./96)*(n**3) - (1./360)*(n**4) - (81./512)*(n**5)
        b2 = (1./48)*(n**2) + (1./15)*(n**3) - (437./1440)*(n**4) + (46./105)*(n**5)
        b3 = (17./480)*(n**3) - (37./840)*(n**4) - (209./4480)*(n**5)
        b4 = (4397./161280)*(n**4) - (11./504)*(n**5)
        b5 = (4583./161280)*(n**5)
        return np.array([b0, b1, b2, b3, b4, b5])
    
    def delta_array(n):
        d0 = np.nan # dummy
        d1 = 2.*n - (2./3)*(n**2) - 2.*(n**3) + (116./45)*(n**4) + (26./45)*(n**5) - (2854./675)*(n**6)
        d2 = (7./3)*(n**2) - (8./5)*(n**3) - (227./45)*(n**4) + (2704./315)*(n**5) + (2323./945)*(n**6)
        d3 = (56./15)*(n**3) - (136./35)*(n**4) - (1262./105)*(n**5) + (73814./2835)*(n**6)
        d4 = (4279./630)*(n**4) - (332./35)*(n**5) - (399572./14175)*(n**6)
        d5 = (4174./315)*(n**5) - (144838./6237)*(n**6)
        d6 = (601676./22275)*(n**6)
        return np.array([d0, d1, d2, d3, d4, d5, d6])
    
    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999 
    a = 6378137.
    F = 298.257222101
    
    # (1) n, A_i, beta_i, delta_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    beta_array = beta_array(n)
    delta_array = delta_array(n)
        
    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) )
    
    # (3) xi, etaの計算
    xi = (x + S_) / A_
    eta = y / A_

    # (4) xi', eta'の計算
    xi2 = xi - np.sum(np.multiply(beta_array[1:], 
                                  np.multiply(np.sin(2*xi*np.arange(1,6)),
                                              np.cosh(2*eta*np.arange(1,6)))))
    eta2 = eta - np.sum(np.multiply(beta_array[1:],
                                   np.multiply(np.cos(2*xi*np.arange(1,6)),
                                               np.sinh(2*eta*np.arange(1,6)))))
    
    # (5) chiの計算
    chi = np.arcsin( np.sin(xi2)/np.cosh(eta2) ) # [rad]
    latitude = chi + np.dot(delta_array[1:], np.sin(2*chi*np.arange(1, 7))) # [rad]

    # (6) 緯度(latitude), 経度(longitude)の計算
    longitude = lambda0_rad + np.arctan( np.sinh(eta2)/np.cos(xi2) ) # [rad]
    
    # ラジアンを度になおしてreturn
    return round(np.rad2deg(latitude), 8), round(np.rad2deg(longitude), 8) # [deg]


def main():
    parser = argparse.ArgumentParser(
        description="ExcelからGeoJSONを生成するプログラム（L側・R側の座標＋幅員、calc_lot_lanで変換、各ポイントのプロパティに座標番号、緯度経度、幅員を表示）"
    )
    parser.add_argument("excel", help="入力Excelファイルのパス")
    parser.add_argument("output", help="出力GeoJSONファイルのパス")
    args = parser.parse_args()

    all_features = []
    
    try:
        excel_file = pd.ExcelFile(args.excel)
    except Exception as e:
        print(f"Excelファイルの読み込みエラー: {e}", file=sys.stderr)
        sys.exit(1)

    for sheet in excel_file.sheet_names:
        if sheet == 'Sheet1' or sheet == 'Restored': continue
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet)
        except Exception as e:
            print(f"シート '{sheet}' の読み込みエラー: {e}", file=sys.stderr)
            continue
    
        left_features = []
        right_features = []
        
        # 各行ごとに左側・右側のデータを処理
        for idx, row in df.iterrows():
            try:
                # 左側の処理：座標番号が空でない場合のみ処理
                l_num = row["L-座標番号"]
                if not (pd.isnull(l_num) or str(l_num).strip() == ""):
                    orig_l_x = float(row["L-X座標"])
                    orig_l_y = float(row["L-Y座標"])
                    new_l_lat, new_l_lon = calc_lat_lon(orig_l_x, orig_l_y)
                    left_features.append({
                        "geometry": [new_l_lon, new_l_lat],
                        "properties": {
                            "路線名": sheet.replace('+', ''),
                            "図面番号": row["図面番号"],
                            "座標番号": l_num,
                            "X座標": orig_l_x,
                            "Y座標": orig_l_y,
                            "L側幅員": "" if pd.isnull(row["L-幅員"]) else row["L-幅員"],
                            "備考": "" if pd.isnull(row["L-備考"]) else row["L-備考"]
                        }
                    })
                
                # 右側の処理：座標番号が空でない場合のみ処理
                r_num = row["R-座標番号"]
                if not (pd.isnull(r_num) or str(r_num).strip() == ""):
                    orig_r_x = float(row["R-X座標"])
                    orig_r_y = float(row["R-Y座標"])
                    new_r_lat, new_r_lon = calc_lat_lon(orig_r_x, orig_r_y)
                    right_features.append({
                        "geometry": [new_r_lon, new_r_lat],
                        "properties": {
                            "路線名": sheet.replace('+', ''),
                            "図面番号": row["図面番号"],
                            "座標番号": r_num,
                            "X座標": orig_r_x,
                            "Y座標": orig_r_y,
                            "R側幅員": "" if pd.isnull(row["R-幅員"]) else row["R-幅員"],
                            "備考": "" if pd.isnull(row["R-備考"]) else row["R-備考"]
                        }
                    })
                # print(f"シート '{sheet}' の行 {idx} の変換")
            except Exception as e:
                print(f"シート '{sheet}' の行 {idx} の変換エラー: {e}", file=sys.stderr)

        if not left_features or not right_features:
            print("十分な座標データがありません", file=sys.stderr)
            sys.exit(1)
        
        # ポリゴンの座標リスト作成
        # 左側をファイル内順（昇順）に、続いて右側を逆順（降順）に連結し、最初の左側座標で閉じる
        left_coords = [feat["geometry"] for feat in left_features]
        right_coords = [feat["geometry"] for feat in right_features]
        polygon_coords = left_coords + right_coords[::-1] + [left_coords[0]]
        
        polygon_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coords]
            },
            "properties": {
                "路線名": sheet  # シート名をプロパティとして記録
            }
        }
        all_features.append(polygon_feature)
        
        # ポリゴンの頂点順に合わせて、左側（そのまま）＋右側（逆順）の順で各点 Feature を作成
        polygon_point_features = left_features + right_features[::-1]
        for feat in polygon_point_features:
            point_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": feat["geometry"]
                },
                "properties": feat["properties"]
            }
            all_features.append(point_feature)

    if not all_features:
        print("有効なシートが見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"GeoJSONファイルの出力エラー: {e}", file=sys.stderr)
        sys.exit(1)
    
    # print(f"GeoJSONファイルが正常に出力されました: {args.output}")

if __name__ == "__main__":
    main()