import os, time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def download_excel(download_path):

    os.makedirs(download_path, exist_ok = True)

    for file in os.listdir(download_path):
        if file.endswith(".xlsx"):
            os.remove(os.path.join(download_path, file))

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_experimental_option("prefs", {
        "download.default_directory" : download_path,
        "download.prompt_for_download" : False,
        "directory_upgrade" : True
    })

    driver = webdriver.Chrome(options = options)

    driver.get("https://poisonmap.mfds.go.kr/reference.do")

    try:

        wait = WebDriverWait(driver, 10)

        download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='downloadExcel()']")))
        
        driver.execute_script("arguments[0].click();", download_button)

    except Exception as e:
        print(e)

    def wait_for_download_complete(path, timeout = 30):

        second = 0

        while second < timeout:

            file = os.listdir(path)

            downloading = [f for f in file if f.endswith(".crdownload")]

            if not downloading and any(f.endswith(".xlsx") for f in file):
                return
            
            time.sleep(1)

            second += 1

        raise TimeoutError("제한 시간 초과")

    wait_for_download_complete(download_path)

    driver.quit()

def get_excel_file(download_path):

    file = [f for f in os.listdir(download_path) if f.endswith(".xlsx")]

    if not file:
        raise FileNotFoundError("파일을 찾을 수 없습니다.")
    
    return max([os.path.join(download_path, f) for f in file], key = os.path.getctime)

def read_excel_file(file_path):

    df = pd.read_excel(file_path)

    exclude_cols = ['14시 기준 온도', '14시 기준 습도', '14시 기준 강수량', '미세먼지']

    df = df.drop(columns = [col for col in exclude_cols if col in df.columns])

    df = df.rename(columns = {'예측지수' : '식중독_예측지수'})

    agg_dictionary = {
        col : ('mean' if col == '식중독_예측지수' else (lambda x : x.mode().iloc[0] if not x.mode().empty else x.iloc[0]))
        for col in df.columns if col not in ['시도', '시군구']
    }

    df = df.groupby(['시도', '시군구'], as_index = False).agg(agg_dictionary)

    return df