import os
import sys
import time
import json
import re
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


try:
    from webdriver_manager.chrome import ChromeDriverManager
    _HAS_WDM = True
except Exception:
    _HAS_WDM = False

# =====================================================
# CONFIG
# =====================================================
EMAIL = "jianbiao0404@gmail.com"
PASSWORD = "biao9119"

MAX_WAIT = 90
POLL_INTERVAL = 0.5

TARGET_URL = "https://watch.tonton.com.my/live/8tv"

M3U8_RE = re.compile(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', re.IGNORECASE)


# =====================================================
# HELPERS
# =====================================================
def now():
    return time.strftime("%H:%M:%S")


def find_chromedriver():
    env_path = os.getenv("CHROMEDRIVER_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    path = shutil.which("chromedriver")
    if path:
        return path

    if _HAS_WDM:
        try:
            return ChromeDriverManager().install()
        except Exception:
            pass

    return None


# =====================================================
# CREATE DRIVER
# =====================================================
def make_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    chrome_options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL"}
    )

    driver_path = find_chromedriver()
    service = Service(driver_path) if driver_path else Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(120)

    return driver


# =====================================================
# MAIN
# =====================================================
def main():
    if not EMAIL or not PASSWORD:
        raise Exception("Missing TONTON_EMAIL or TONTON_PASSWORD")

    print(f"{now()} Starting capture")
    driver = make_driver()

    # Enable network logs
    try:
        driver.execute_cdp_cmd("Network.enable", {})
    except Exception:
        pass

    # Open homepage
    print(f"{now()} Opening homepage")
    driver.get("https://www.tonton.com.my")
    time.sleep(8)

        # Click Sign In
    print(f"{now()} Opening login")
    driver.find_element(By.XPATH, "//span[contains(text(),'Sign In')]").click()
    time.sleep(8)

        # Switch popup
    handles = driver.window_handles
    if len(handles) > 1:
            driver.switch_to.window(handles[-1])

    time.sleep(5)

        # Login
    driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').send_keys(EMAIL)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(PASSWORD)

    time.sleep(1)
    driver.find_element(By.ID, "submitBtn").click()

    print(f"{now()} Logged in")
    time.sleep(10)

        # Back to main window
    driver.switch_to.window(handles[0])

        # Open live page
    print(f"{now()} Opening stream")
    driver.get(TARGET_URL)
    time.sleep(10)

        # Try force play
    try:
            driver.execute_script("""
                let v = document.querySelector('video');
                if (v) {
                    v.muted = true;
                    v.play();
                }
            """)
            print(f"{now()} Triggered video play")
    except Exception:
            pass

    time.sleep(5)



# =====================================================
# START
# =====================================================
if __name__ == "__main__":
    main()
