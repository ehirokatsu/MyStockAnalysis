import yfinance as yf
import pandas as pd
import datetime as dt
import os
import logging

# ログディレクトリ作成
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 日付を取得してログファイルのパスを設定
today = dt.datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_dir, f"{today}.log")

# ログ設定
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def send_imessage(phone_number, message):
    """iMessageを送信"""
    try:
        os.system(f'osascript -e \'tell application "Messages" to send "{message}" to buddy "{phone_number}"\'')
        logging.info(f"iMessageを {phone_number} に送信しました。")
    except Exception as e:
        logging.error(f"iMessageの送信に失敗しました: {e}")

def calculate_moving_average(data, days):
    """移動平均線を計算"""
    return data['Close'].rolling(window=days).mean()

def check_condition(close_price, moving_avg):
    """条件をチェック"""
    return float(close_price) < float(moving_avg)

def analyze_stock(symbol, check_days=10, moving_avg_days=50):
    """1つの銘柄のデータを取得・分析"""
    end_date = dt.datetime.now()
    start_date = end_date - dt.timedelta(days=100)

    logging.info(f"{symbol} のデータを取得中...")
    
    stock = yf.Ticker(symbol)
    stock_data = stock.history(start=start_date, end=end_date)

    if stock_data.empty:
        logging.warning(f"{symbol} のデータが見つかりませんでした。")
        return None

    stock_data['MA50'] = calculate_moving_average(stock_data, moving_avg_days)

    try:
        stock_name = stock.info.get('shortName', symbol)
    except Exception:
        stock_name = symbol

    logging.info(f"{symbol} の最新データ:\n{stock_data.tail(3)}")

    is_condition_met = True
    for i in range(1, check_days + 1):
        try:
            close_price = stock_data['Close'].iloc[-i]
            moving_avg = stock_data['MA50'].iloc[-i]

            if pd.isna(close_price) or pd.isna(moving_avg):
                is_condition_met = False
                logging.warning(f"欠損値が存在します: 終値={close_price}, 移動平均={moving_avg}")
                break

            if not check_condition(close_price, moving_avg):
                is_condition_met = False
                logging.info(f"条件未達: 終値={close_price}, 移動平均={moving_avg}")
                break
        except IndexError as e:
            is_condition_met = False
            logging.error(f"インデックスエラー: 十分なデータがありません。エラー詳細: {e}")
            break
        except Exception as e:
            is_condition_met = False
            logging.error(f"予期しないエラーが発生しました: {e}")
            break

    if is_condition_met:
        return f"{stock_name} ({symbol})"
    return None

def main(symbols):
    """複数の銘柄を処理し、まとめて通知を送る"""
    condition_met_stocks = []
    today = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for symbol in symbols:
        result = analyze_stock(symbol)
        if result:
            condition_met_stocks.append(result)

    if condition_met_stocks:
        message = f"{today} の分析結果\n以下の銘柄が50日移動平均線を10日連続で下回りました:\n" + "\n".join(condition_met_stocks)
        send_imessage("e.hirokatsu@icloud.com", message)
        logging.info(message)
    else:
        logging.info(f"{today}: 条件を満たす銘柄はありませんでした。")

if __name__ == "__main__":
    SYMBOLS = [
        "8306.T", "8316.T", "5393.T", "6209.T", "8058.T", "8001.T", "1655.T", "5334.T",
        "6345.T", "9436.T", "7921.T", "6113.T", "2003.T", "5110.T", "1928.T", "4220.T",
        "4762.T", "9986.T", "7981.T", "2163.T", "9433.T", "1835.T", "9600.T", "9769.T",
        "9513.T", "9698.T", "2914.T", "7995.T", "7483.T", "9303.T", "8898.T", "6073.T",
        "4521.T", "9880.T", "3407.T", "9381.T", "1489.T", "8053.T", "9432.T", "7811.T",
        "2169.T", "7820.T"
    ]
    main(SYMBOLS)