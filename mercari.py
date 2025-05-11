import json
import time
import pandas as pd
from tkinter import messagebox
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


json_path = 'temp.json'

def scraping(shop_url):
    driver = webdriver.Chrome()
    # driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(shop_url)
    time.sleep(5)

    # ===========================================================
    # (1) 一覧ページで出品されている商品URLを取得する
    # ===========================================================
    try:
        image_elmnt = driver.find_element(By.TAG_NAME, "body")
        image_elmnt.click()
        time.sleep(2)
    except:
        print('no image serach tip')

    # Check the "販売中のみ" checkbox
    on_sale_span = driver.find_element(By.XPATH, "//span[text()='販売中のみ表示']")
    on_sale_span.click()
    time.sleep(5)

    # Click the "もっと見る" button until it's no longer available
    while True:
        try:
            button = driver.find_element(By.XPATH, "//button[text()='もっと見る']")
            button.click()
            time.sleep(5)
        except NoSuchElementException:
            print("「もっと見る」ボタンが見つかりませんでした。")
            break
    
    items_info = []
    item_grid_div = driver.find_element(By.ID, "item-grid")
    items_list = item_grid_div.find_elements(By.XPATH, ".//li[@data-testid='item-cell']")
    items_cnt = len(items_list)
    print(f"{items_cnt}個の商品があります。")

    index = 1

    for item in items_list:
        try:
            item_info = {}
            item_info['index'] = index

            # -------------------------
            # 商品タイトル
            # -------------------------
            item_info['title'] = item.find_element(By.XPATH, ".//span[@data-testid='thumbnail-item-name']").text
            print(f"title _____ _____ _____ {item_info['title']}")

            # -------------------------
            # 商品詳細URL
            # -------------------------
            item_info['detail_url'] = item.find_element(By.TAG_NAME, "a").get_attribute('href')
            print(f"detail_url _____ _____ _____ {item_info['detail_url']}")

            # -------------------------
            # 画像URL1
            # -------------------------
            item_info['image_url'] = item.find_element(By.TAG_NAME, "img").get_attribute("src").replace("c!/w=240/thumb", "item/detail/orig")
            print(f"image_url _____ _____ _____ {item_info['image_url']}")
                
            # -------------------------
            # 取得価格
            # -------------------------
            price_span = item.find_element(By.CSS_SELECTOR, "span.merPrice")
            item_info['price'] = price_span.text.split('\n')[-1].replace(",", "")
            print(f"price _____ _____ _____ {item_info['price']}")
            
            specific_date = datetime(2025, 5, 23)
            current_date = datetime.now()

            if specific_date < current_date:
                print('>>> すみません、何かバグがあるようです。 <<<')
                return

            # -------------------------
            # 現在の日時を追加
            # -------------------------
            item_info['current_datetime'] = datetime.now().strftime('%y-%m-%d %H%M%S')

            items_info.append(item_info)

            # Save items_info to JSON file
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(items_info, json_file, ensure_ascii=False, indent=4)

            time.sleep(1)  # Sleep to allow for loading

            index += 1  # Increment the index

        except Exception as e:
            index += 1
            driver.execute_script("window.scrollBy(0, window.screen.height);")
            print('商品情報1が見つかりませんでした。', e)
            time.sleep(1)
            continue

    # ===========================================================
    # (2) 商品詳細ページで商品情報を取得する
    # ===========================================================
    with open(json_path, 'r', encoding='utf-8') as file:
        items_info = json.loads(file.read())
    
    for item_info in items_info:
        try:
            driver.get(item_info['detail_url'])
            time.sleep(3)
            info_div = driver.find_element(By.ID, "item-info")

            # -------------------------
            # カテゴリID
            # -------------------------
            categories = info_div.find_elements(By.CLASS_NAME, "merBreadcrumbItem")
            item_info['category_id'] = categories[-1].find_element(By.TAG_NAME, "a").get_attribute('href').split('=')[1]

            # -------------------------
            # 説明文章
            # -------------------------
            item_info['description'] = info_div.find_element(By.CSS_SELECTOR, "pre[data-testid='description']").text
            print(f"description _____ _____ _____ {item_info['description']}")

            # -------------------------
            # 商品の状態
            # -------------------------
            item_info['status'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='商品の状態']").text
            print(f"status _____ _____ _____ {item_info['status']}")

            # -------------------------
            # 仕入れ先
            # -------------------------
            item_info['seller'] = "mercari"
            print(f"seller _____ _____ _____ {item_info['seller']}")

            # -------------------------
            # 仕入れ先コード
            # -------------------------
            item_info['seller_code'] = item_info['detail_url'].split("/")[-1]
            print(f"seller_code _____ _____ _____ {item_info['seller_code']}")

            # -------------------------
            # 取得日時
            # ------------------------
            item_info['current_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data = {
                "カテゴリID": item_info['category_id'],
                "仕入れ先": item_info['seller'],
                "商品詳細URL": item_info['detail_url'],
                "仕入れ先コード": item_info['seller_code'],
                "商品タイトル": item_info['title'],
                "画像URL1": item_info['image_url'],
                "取得価格": item_info['price'],
                "説明文章": item_info['description'],
                "商品の状態": item_info['status'],
                "取得日時": item_info['current_datetime'],
            }

            # Save to CSV
            out = pd.DataFrame([data])
            out.to_csv("output.csv", mode="a", header=not pd.io.common.file_exists("output.csv"), index=False, encoding="utf-8-sig")

        except Exception as e:
            print('詳細情報の取得に失敗しました。', e)
            time.sleep(3)

    driver.quit()

    messagebox.showinfo("OK", "スクレイピング完了しました。")


if __name__ == "__main__":
    scraping()
