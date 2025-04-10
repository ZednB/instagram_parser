import os
import time
import json
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

load_dotenv('.env')

username = os.getenv('username')
password = os.getenv('password')
instagram_url = os.getenv('instagram_url')


def get_instagram_data(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(5)
        try:
            accept_cookies = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Разрешить все')]",))
            )
            driver.execute_script("arguments[0].click();", accept_cookies)
            print("Cookies приняты через JavaScript")
        except Exception as e:
            print("Ошибка при принятии cookies:", e)
        time.sleep(2)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)
    except:
        pass
    time.sleep(5)
    print(url)
    try:
        save_info_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Сохранить данные')]"))
        )
        save_info_button.click()
        print("Данные сохранены")
        time.sleep(5)
    except Exception as e:
        print("Ошибка при сохранении данных:", e)
    try:
        stats = driver.find_elements(By.CSS_SELECTOR, "header section ul li span span")
        for i, el in enumerate(stats):
            print(f"{i}: {el.text}")
        time.sleep(5)
        try:
            posts = stats[0].text  # Количество постов
            followers = stats[2].text  # Количество подписчиков
            following = stats[4].text  # Количество подписок
            print(f"Постов: {posts}, Подписчиков: {followers}, Подписок: {following}")
            posts_data = []
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            post_links = []
            post_elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/") and @role="link"]')
            for el in post_elements:
                time.sleep(3)
                href = el.get_attribute("href")
                if href and href not in post_links:
                    time.sleep(3)
                    post_links.append(href)

            if not post_links:
                print("❌ Посты не найдены. Возможно, страница еще не догрузилась или требуется скроллинг.")
            else:
                print(f"🔍 Найдено постов: {len(post_links)}")

            # Обработка каждого поста
            for post_url in post_links:
                driver.get(post_url)
                print("post_url:", post_url)
                time.sleep(5)
                try:
                    caption = driver.find_element(By.CSS_SELECTOR, 'h1').text
                except:
                    caption = 'Нет описания'
                try:
                    likes_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//span[contains(text(),"отметок")]'))
                    )
                    likes_text = likes_element.text
                    print("Текст с лайками:", likes_text)
                    # Например, "31 отметок "Нравится"" -> "31"
                    likes = likes_text.split()[0]
                except Exception as e:
                    print("Ошибка при получении лайков:", e)
                    likes = '0'
                try:
                    comments = len(driver.find_elements(By.CSS_SELECTOR, 'ul li'))
                except:
                    comments = '0'
                try:
                    date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                except:
                    date = 'Неизвестно'
                print(f"Описание: {caption}, Лайки: {likes}, Комментарии: {comments}, Дата публикации: {date}")
                posts_data.append([caption, likes, comments, date])
                print(caption, likes, comments, date)
            profile_data = {
                'Подписчики': int(followers.replace(',', '')),
                'Публикации': int(posts.replace(',', ''))
            }
            with open('profile_data.json', 'w', encoding='utf-8') as json_file:
                json.dump(profile_data, json_file, ensure_ascii=False, indent=4)
            print('Данные сохранены в JSON файл')
            print(profile_data, json_file)

            with open('posts.csv', 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['Описание поста', 'Лайки', 'Комментарии', 'Дата публикации'])
                writer.writerows(posts_data)
            print('Данные сохранены в CSV файл')
            return posts, followers, following
        except IndexError:
            print("Ошибка: не удалось получить данные!")
    except Exception as e:
        print("Ошибка при получении статистики:", e)
        return None
    finally:
        driver.quit()


get_instagram_data(instagram_url)
