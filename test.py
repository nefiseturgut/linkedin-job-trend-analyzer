# linkedin_jobs_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def start_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument('--headless=new')  # headless mode
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    # User agent değişimi risk yaratabilir; dikkatli kullanın
    # opts.add_argument('user-agent=YourUserAgentHere')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    return driver

def scrape_jobs(query='data scientist', location='Turkey', pages=1):
    driver = start_driver(headless=False)  # geliştirme için headless=False önerilir
    wait = WebDriverWait(driver, 15)
    results = []

    base_url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ','%20')}&location={location.replace(' ','%20')}"
    driver.get(base_url)

    for page in range(pages):
        # sayfa yüklenmesini bekle
        time.sleep(2)
        # iş kartlarını seç (selectorlar değişebilir)
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.jobs-search__results-list li")))
        for c in cards:
            try:
                title = c.find_element(By.CSS_SELECTOR, "h3").text.strip()
                company = c.find_element(By.CSS_SELECTOR, "h4").text.strip()
                # location ve link - selectorlar farklı olabilir
                loc = c.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
                link = c.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                # ilan detay sayfasını açıp kısa açıklama çekme
                # alternatif: card içinden kısa açıklama al
                results.append({
                    "title": title,
                    "company": company,
                    "location": loc,
                    "url": link
                })
            except Exception as e:
                # element okunamadıysa atla
                continue

        # pagination: next butonuna tıkla (eğer varsa)
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
            if 'disabled' in next_btn.get_attribute('class'):
                break
            next_btn.click()
            time.sleep(2)
        except:
            break

    driver.quit()
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = scrape_jobs(query="machine learning engineer", location="Istanbul, Turkey", pages=2)
    print(df.head())
    df.to_csv("linkedin_jobs_sample.csv", index=False)
