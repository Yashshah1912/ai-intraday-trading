import yfinance as yf
import ta
import smtplib
from email.message import EmailMessage
from telegram import Bot

# 🔐 Credentials (private & secure)
TELEGRAM_BOT_TOKEN = '7651952387:AAHvfHMWid5C1nvCEjWVNeeiIywjx8eMKY4'
TELEGRAM_USER_ID = 5675680125
EMAIL_SENDER = 'YashShah7684@gmail.com'
EMAIL_PASSWORD = 'jjjzzoktzhxrduuu'
EMAIL_RECEIVER = 'YashShah7684@gmail.com'

# 🧾 Indian stocks to scan
stock_list = ['RELIANCE.NS', 'ICICIBANK.NS', 'HDFCBANK.NS', 'INFY.NS', 'TCS.NS']

# 🚀 Telegram function
def send_telegram(message):
    Bot(token=TELEGRAM_BOT_TOKEN).send_message(chat_id=TELEGRAM_USER_ID, text=message)

# 📧 Gmail function
def send_email(body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = '📡 Intraday Stock Signal Alert'
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

# 🔍 Scanning function
def scan_stocks():
    alerts = []
    for stock in stock_list:
        data = yf.download(stock, period='2d', interval='5m')
        if data.empty:
            continue
        df = data.copy()

        # VWAP
        df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
            high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']
        ).vwap

        # RSI (fixed to ensure 1D Series)
        df['rsi'] = ta.momentum.RSIIndicator(close=df['Close'].squeeze()).rsi()

        # Hammer pattern logic
        last = df.iloc[-1]
        body = abs(last['Close'] - last['Open'])
        range_ = last['High'] - last['Low']
        lower_shadow = min(last['Open'], last['Close']) - last['Low']
        is_hammer = lower_shadow > 2 * body and body / range_ < 0.3

        # Signal condition
        if last['Close'] > last['vwap'] and last['rsi'] < 60 and is_hammer:
            alerts.append(f"📈 {stock} | VWAP breakout + RSI({last['rsi']:.1f}) + Hammer")

    # Send alert or no signal message
    if alerts:
        message = '\n'.join(alerts)
        send_telegram(message)
        send_email(message)
    else:
        send_telegram("❌ No trade signals this cycle.")
        send_email("❌ No trade signals this cycle.")

# 🚦 Run the scanner
scan_stocks()
