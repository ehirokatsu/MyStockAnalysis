import yfinance as yf
import pandas as pd
import datetime as dt
import os

def send_imessage(phone_number, message):
    """iMessageを送信"""
    try:
        os.system(f'osascript -e \'tell application "Messages" to send "{message}" to buddy "{phone_number}"\'')
        print(f"iMessageを{phone_number}に送信しました。")
    except Exception as e:
        print(f"iMessageの送信に失敗しました: {e}")



# 銘柄コード設定
KDDI_SYMBOL = "7820.T"  # KDDIのYahoo Financeシンボル
CHECK_DAYS = 10  # 条件を連続して満たす必要のある日数
MOVING_AVERAGE_DAYS = 50  # 移動平均線の期間

def calculate_moving_average(data, days):
    """移動平均線を計算"""
    return data['Close'].rolling(window=days).mean()


def send_notification(message):
    """Macの通知センターに通知を送る"""
    os.system(f"osascript -e 'display notification \"{message}\" with title \"株価通知\"'")

def check_condition(kddi_close, kddi_ma50):
    """条件をチェック"""
    # 値を float に変換し比較
    return float(kddi_close) < float(kddi_ma50)

def main():
    # 使用例
    # send_imessage("+819032717248", "KDDIの株価が条件を満たしました！2")
    send_imessage("e.hirokatsu@icloud.com", "KDDIの株価が条件を満たしました！3")



    # 現在の日付を取得
    end_date = dt.datetime.now()
    # 過去100日間のデータを取得
    start_date = end_date - dt.timedelta(days=100)

    # データを取得
    print(f"KDDI ({KDDI_SYMBOL}) のデータを取得中...")
    kddi_data = yf.download(KDDI_SYMBOL, start=start_date, end=end_date)

    if kddi_data.empty:
        print("KDDIのデータが見つかりませんでした。")
        return

    # 50日移動平均線を計算
    kddi_data['MA50'] = calculate_moving_average(kddi_data, MOVING_AVERAGE_DAYS)
    print(kddi_data.tail(10))  # データ確認用

    # 過去10日間の条件チェック
    is_condition_met = True
    for i in range(1, CHECK_DAYS + 1):
        try:
            # 終値と50日移動平均線の値を取得
            kddi_close = kddi_data['Close'].iloc[-i]  # ilocで特定の行を取得
            kddi_ma50 = kddi_data['MA50'].iloc[-i]

            # デバッグ用の型と値を出力
            print(f"kddi_closeの型: {type(kddi_close)}, 値: {kddi_close}")
            print(f"kddi_ma50の型: {type(kddi_ma50)}, 値: {kddi_ma50}")

            # `kddi_close`を単一値に変換
            if isinstance(kddi_close, pd.Series):
                kddi_close = kddi_close.item()  # または `kddi_close.values[0]`

            # 欠損値のチェック
            if pd.isna(kddi_close) or pd.isna(kddi_ma50):
                is_condition_met = False
                print(f"欠損値が存在します: kddi_close={kddi_close}, kddi_ma50={kddi_ma50}")
                break

            # 条件をチェック（単一値として評価）
            if not check_condition(kddi_close, kddi_ma50):
                is_condition_met = False
                print(f"条件未達: 終値={kddi_close}, 移動平均={kddi_ma50}")
                break
        except IndexError as e:
            is_condition_met = False
            print(f"インデックスエラー: 十分なデータがありません。エラー詳細: {e}")
            break
        except Exception as e:
            is_condition_met = False
            print(f"予期しないエラーが発生しました: {e}")
            break

    # 条件が満たされていれば通知
    if is_condition_met:
        send_notification(f"KDDIの株価が50日移動平均線を{CHECK_DAYS}日連続で下回りました！")
        print(f"KDDIの株価が50日移動平均線を{CHECK_DAYS}日連続で下回りました！")
    else:
        print("条件はまだ満たされていません。")

if __name__ == "__main__":
    main()