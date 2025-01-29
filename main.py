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

def calculate_moving_average(data, days):
    """移動平均線を計算"""
    return data['Close'].rolling(window=days).mean()

def check_condition(close_price, moving_avg):
    """条件をチェック"""
    return float(close_price) < float(moving_avg)

def analyze_stock(symbol, check_days=10, moving_avg_days=50):
    """1つの銘柄のデータを取得・分析"""
    # 現在の日付を取得
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=100)

    # データを取得
    print(f"{symbol} のデータを取得中...")
    stock = yf.Ticker(symbol)
    stock_data = stock.history(start=start_date, end=end_date)

    if stock_data.empty:
        print(f"{symbol} のデータが見つかりませんでした。")
        return

    # 50日移動平均線を計算
    stock_data['MA50'] = calculate_moving_average(stock_data, moving_avg_days)

    # 銘柄名を取得
    try:
        stock_name = stock.info.get('shortName', symbol)  # 取得できない場合はシンボルを代用
    except Exception:
        stock_name = symbol

    print(stock_data.tail(10))  # データ確認用

    # 過去10日間の条件チェック
    is_condition_met = True
    for i in range(1, check_days + 1):
        try:
            close_price = stock_data['Close'].iloc[-i]
            moving_avg = stock_data['MA50'].iloc[-i]

            if pd.isna(close_price) or pd.isna(moving_avg):
                is_condition_met = False
                print(f"欠損値が存在します: 終値={close_price}, 移動平均={moving_avg}")
                break

            if not check_condition(close_price, moving_avg):
                is_condition_met = False
                print(f"条件未達: 終値={close_price}, 移動平均={moving_avg}")
                break
        except IndexError as e:
            is_condition_met = False
            print(f"インデックスエラー: 十分なデータがありません。エラー詳細: {e}")
            break
        except Exception as e:
            is_condition_met = False
            print(f"予期しないエラーが発生しました: {e}")
            break

    if is_condition_met:
        message = f"{stock_name} ({symbol}) の株価が50日移動平均線を{check_days}日連続で下回りました！"
        send_imessage("e.hirokatsu@icloud.com", message)
        print(message)
    else:
        print(f"{stock_name} の条件はまだ満たされていません。")

def main(symbols):
    """複数の銘柄を処理"""
    for symbol in symbols:
        analyze_stock(symbol)

if __name__ == "__main__":
    SYMBOLS = ["2169.T", "7820.T"]  # ここに複数の銘柄コードを指定
    main(SYMBOLS)


# ログ出力　銘柄、移動平均日数指定の外部ファイル化