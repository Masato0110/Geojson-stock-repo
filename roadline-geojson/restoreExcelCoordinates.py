import pandas as pd
import sys

def parse_float(value):
    """カンマを除去して float に変換する"""
    return str(value).replace(",", "").replace(" ", "")

def restore_value(val, ref):
    """
    val: セルに記載された値（文字列として "094.998" など、先頭に 0 が含まれる可能性あり）
    ref: 前行（または最初の完全な値）の確定値 (float)
    
    例:
      ref = -56121.838  → リファレンスの整数部は "56121" (桁数5)
      val = "087.018"    → val の整数部は "087" (文字列としては長さ3)
      → missing = 5 - 3 = 2、リファレンスの先頭2桁 "56" を補う
      → 結果: "-56087.018"
      
    ※ すでに絶対値が十分大きい負数（例: -93534.579）はそのまま返す
    """
    # 文字列として扱う（前後の空白除去）
    val_str = str(val).strip()
    ref_str = str(ref).strip()

    try:
        # すでに完全な値とみなせる場合はそのまま返す
        if val_str.startswith('-') and abs(float(val_str)) >= 10000:
            return float(val_str)
    except Exception:
        pass

    # val を整数部と小数部に分離
    if '.' in val_str:
        val_int_raw, val_frac = val_str.split('.', 1)
    else:
        val_int_raw, val_frac = val_str, ''

    # もし val_int_raw が符号付きなら、符号を記録して除去
    negative = False
    if val_int_raw.startswith('-'):
        negative = True
        val_int_raw = val_int_raw[1:]

    # **ここで、val_int_raw の長さはそのまま使う**
    len_val = len(val_int_raw)  # 例: "087" → 3 (先頭の 0 をそのままカウント)

    # ref の整数部（符号除去）
    ref_int_str = ref_str.split('.')[0].lstrip('-')
    len_ref = len(ref_int_str)  # 例: "56121" → 5

    # 補完すべき桁数は、ref の桁数から val_int_raw の桁数を引く
    missing = len_ref - len_val
    if missing < 0:
        missing = 0
    prefix = ref_int_str[:missing]  # 例: 5 - 3 = 2 → ref_int_str[:2] = "56"

    new_int = prefix + val_int_raw  # 例: "56" + "087" = "56087"
    sign = '-' if (float(ref) < 0 or negative) else ''
    
    if val_frac:
        restored_str = f"{sign}{new_int}.{val_frac}"
    else:
        restored_str = f"{sign}{new_int}"
    
    try:
        return float(restored_str)
    except ValueError:
        try:
            return float(val_str)
        except Exception:
            return float(ref_str)



def main():
    excel_path = "千歳出張所管内.xlsx"  # ファイル名を適宜変更
    sheet_name = "Sheet1"      # シート名も必要に応じて変更
    
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
    except Exception as e:
        print(f"Excel 読み込みエラー: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 列名（実際のExcelの列名に合わせてください）
    r_x_col = "R-X"
    r_y_col = "R-Y"
    l_x_col = "L-X"
    l_y_col = "L-Y"
    
    # 復元後の値を格納する列名
    rx_restored_col = "R-X(復元)"
    ry_restored_col = "R-Y(復元)"
    lx_restored_col = "L-X(復元)"
    ly_restored_col = "L-Y(復元)"
    
    # 新しい列を作成
    df[rx_restored_col] = None
    df[ry_restored_col] = None
    df[lx_restored_col] = None
    df[ly_restored_col] = None
    
    # R 側と L 側それぞれのリファレンスを独立に管理
    ref_rx = None
    ref_ry = None
    ref_lx = None
    ref_ly = None
    
    for idx, row in df.iterrows():
        # ---- R 側 ----
        r_x_val = row.get(r_x_col)
        r_y_val = row.get(r_y_col)
        if pd.notnull(r_x_val) and pd.notnull(r_y_val):
            try:
                orig_rx = parse_float(r_x_val)
                orig_ry = parse_float(r_y_val)
                
                if ref_rx is None:
                    ref_rx = orig_rx
                if ref_ry is None:
                    ref_ry = orig_ry
                
                restored_rx = restore_value(orig_rx, ref_rx)
                ref_rx = restored_rx  # リファレンス更新
                restored_ry = restore_value(orig_ry, ref_ry)
                ref_ry = restored_ry
                
                df.at[idx, rx_restored_col] = restored_rx
                df.at[idx, ry_restored_col] = restored_ry
            except Exception as e:
                print(f"R 側 行 {idx} のエラー: {e}", file=sys.stderr)
        
        # ---- L 側 ----
        l_x_val = row.get(l_x_col)
        l_y_val = row.get(l_y_col)
        if pd.notnull(l_x_val) and pd.notnull(l_y_val):
            try:
                orig_lx = parse_float(l_x_val)
                orig_ly = parse_float(l_y_val)
                
                if ref_lx is None:
                    ref_lx = orig_lx
                if ref_ly is None:
                    ref_ly = orig_ly
                
                restored_lx = restore_value(orig_lx, ref_lx)
                ref_lx = restored_lx
                restored_ly = restore_value(orig_ly, ref_ly)
                ref_ly = restored_ly
                
                df.at[idx, lx_restored_col] = restored_lx
                df.at[idx, ly_restored_col] = restored_ly
            except Exception as e:
                print(f"L 側 行 {idx} のエラー: {e}", file=sys.stderr)
    
    # 結果の表示または保存
    # print(df[[r_x_col, r_y_col, rx_restored_col, ry_restored_col,
    #           l_x_col, l_y_col, lx_restored_col, ly_restored_col]])
    output_sheet = "Restored"  # 追加するシート名

    with pd.ExcelWriter(excel_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        df.to_excel(writer, sheet_name=output_sheet, index=False)

if __name__ == "__main__":
    main()
