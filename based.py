from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

DELAY_SECONDS = 30
REFRESH_MINUTES = 5

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎨 WPLACE AUTO PAINTER 🎨                   ║
║                           v2.0 Pro                          ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_config():
    print("┌─────────────── CONFIGURATION ───────────────┐")
    print(f"│ Paint Interval:  {DELAY_SECONDS} seconds                     │")
    print(f"│ Auto Refresh:    Every {REFRESH_MINUTES} minutes              │")
    print("└──────────────────────────────────────────────┘")
    print()

def print_status(message, status_type="info"):
    icons = {
        "success": "✅",
        "error": "❌", 
        "info": "ℹ️",
        "warning": "⚠️",
        "paint": "🎨",
        "refresh": "🔄",
        "timer": "⏰"
    }
    icon = icons.get(status_type, "•")
    print(f"{icon} {message}")

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except:
        print_status("ChromeDriver installation failed, trying default...", "warning")
        driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def click_canvas_center(driver):
    try:
        window_width = driver.execute_script("return window.innerWidth")
        window_height = driver.execute_script("return window.innerHeight")
        
        center_x = window_width // 2
        center_y = window_height // 2
        
        actions = ActionChains(driver)
        actions.move_by_offset(center_x, center_y)
        actions.click()
        actions.move_by_offset(-center_x, -center_y)
        actions.perform()
        
        return True
    except:
        return False

def click_initial_paint_button(driver):
    try:
        paint_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Paint')]"))
        )
        paint_button.click()
        return True
    except:
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Paint" in button.text:
                    button.click()
                    return True
        except:
            return False
        return False

def click_final_paint_button(driver):
    try:
        paint_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and .//div[contains(text(), 'Paint')]]"))
        )
        paint_button.click()
        return True
    except:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn-primary")
            for button in buttons:
                if "Paint" in button.text:
                    button.click()
                    return True
        except:
            return False
        return False

def perform_paint_sequence(driver):
    print_status("Executing paint sequence...", "paint")
    
    step1 = click_canvas_center(driver)
    if step1:
        time.sleep(1)
    
    step2 = click_initial_paint_button(driver)
    if step2:
        time.sleep(1)
    
    step3 = click_final_paint_button(driver)
    
    success_count = sum([step1, step2, step3])
    
    if success_count == 3:
        print_status("Paint sequence completed successfully!", "success")
        return True
    else:
        print_status(f"Paint sequence failed ({success_count}/3 steps)", "error")
        return False

def countdown_timer(seconds, action_name):
    for remaining in range(seconds, 0, -1):
        mins = remaining // 60
        secs = remaining % 60
        if mins > 0:
            print(f"\r⏳ {action_name} in {mins}m {secs:02d}s", end="", flush=True)
        else:
            print(f"\r⏳ {action_name} in {secs:02d}s", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50 + "\r", end="")

def wait_for_site_load(driver):
    try:
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )
        
        return True
    except:
        return False

def main():
    clear_screen()
    print_banner()
    print_config()
    
    print_status("Initializing browser...", "info")
    driver = setup_driver()
    
    try:
        print_status("Loading wplace.live...", "info")
        driver.get("https://wplace.live")
        
        if not wait_for_site_load(driver):
            print_status("Failed to load site properly", "error")
            return
        
        print_status("Site loaded successfully", "success")
        print()
        print("┌────────────────────────────────────────┐")
        print("│  Please login and prepare the site    │") 
        print("│  Auto-painter will start shortly...   │")
        print("└────────────────────────────────────────┘")
        print()
        countdown_timer(45, "Starting automation")
        
        clear_screen()
        print_banner()
        print_status("🚀 AUTOMATION ACTIVE", "success")
        print("Press Ctrl+C to stop")
        print("═" * 50)
        print()
        
        refresh_counter = 0
        paint_count = 0
        max_cycles_before_refresh = (REFRESH_MINUTES * 60) // DELAY_SECONDS
        
        while True:
            try:
                success = perform_paint_sequence(driver)
                if success:
                    paint_count += 1
                    print_status(f"Paint #{paint_count} completed", "success")
                else:
                    print_status("Paint attempt failed", "error")
                
                refresh_counter += 1
                
                if refresh_counter >= max_cycles_before_refresh:
                    print()
                    print_status(f"Auto-refreshing page (every {REFRESH_MINUTES}min)", "refresh")
                    driver.refresh()
                    if wait_for_site_load(driver):
                        print_status("Page refreshed successfully", "success")
                        countdown_timer(10, "Resuming automation")
                    else:
                        print_status("Page refresh failed, continuing...", "warning")
                    refresh_counter = 0
                    print()
                
                cycles_until_refresh = max_cycles_before_refresh - refresh_counter
                time_until_refresh = cycles_until_refresh * DELAY_SECONDS
                mins_until_refresh = time_until_refresh // 60
                
                if mins_until_refresh > 0:
                    print_status(f"Next refresh in ~{mins_until_refresh} minutes", "timer")
                
                countdown_timer(DELAY_SECONDS, "Next paint")
                
            except KeyboardInterrupt:
                print()
                print("═" * 50)
                print_status("Automation stopped by user", "info")
                print_status(f"Total paints completed: {paint_count}", "info")
                break
            except Exception as e:
                print_status(f"Unexpected error: {e}", "error")
                countdown_timer(DELAY_SECONDS, "Retrying")
                
    finally:
        print_status("Closing browser...", "info")
        driver.quit()
        print()
        print("╔══════════════════════════════════════════════╗")
        print("║            Thanks for using Auto-Painter!   ║")
        print("╚══════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()