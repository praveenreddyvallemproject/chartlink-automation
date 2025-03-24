from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import schedule
import telegram
import pyperclip
import os

# Environment Variables for Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Chartlink Screener
SCREENER_TEXT = """nifty 500 ( ( nifty 500 ( latest open > 180 and latest volume > 100000 and latest close > 1 day ago close and( nifty 500 ( ( nifty 500 ( latest ema( close,5 ) > latest ema( close,20 ) and latest ema( close,20 ) > latest sma( close,40 ) ) ) or( nifty 500 ( latest adx di positive( 14 ) > latest adx di negative( 14 ) and latest adx( 14 ) > 25 and latest adx di positive( 14 ) > 25 ) ) or( nifty 500 ( 1 day ago close > 2 days ago close and 2 days ago close > 3 days ago close and 3 days ago close > 4 days ago close ) ) or( nifty 500 ( latest rsi( 14 ) > 30 and latest rsi( 14 ) < 60 ) ) or( nifty 500 ( latest macd line( 26,12,9 ) > latest macd signal( 26,12,9 ) and latest macd line( 26,12,9 ) > 0 ) ) ) ) ) ) )"""

# Initialize Telegram Bot
bot = telegram.Bot(token=BOT_TOKEN)

# Headless Chrome Setup
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # No GUI
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

# Automation Function
def run_chartlink_automation():
    driver = get_driver()
    driver.maximize_window()
    driver.get("https://www.chartink.com/")
    
    try:
        # Paste Screener
        paste_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )
        paste_input.clear()
        paste_input.send_keys(SCREENER_TEXT)
        
        # Click Run Button
        run_button = driver.find_element(By.CLASS_NAME, "btn-success")
        run_button.click()
        
        # Wait for Results
        time.sleep(10)
        
        # Click Copy Button
        copy_button = driver.find_element(By.CLASS_NAME, "btn-primary")
        copy_button.click()
        
        # Get Copied Data
        stock_list = pyperclip.paste()
        
        # Send to Telegram
        if stock_list:
            bot.send_message(chat_id=CHAT_ID, text=f"📈 *Today's Stocks:* \n\n{stock_list}", parse_mode='Markdown')
            print("✅ Stock list sent to Telegram.")
        else:
            print("⚠️ No data found.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        driver.quit()

# Schedule Job for Daily Run
schedule.every().day.at("09:15").do(run_chartlink_automation)

# Run the Job Until 12:00 PM
end_time = "12:00"
while True:
    current_time = time.strftime("%H:%M")
    if current_time >= end_time:
        break
    schedule.run_pending()
    time.sleep(60)
