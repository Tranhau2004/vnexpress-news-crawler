import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import schedule
import os

BASE_URL = "https://vnexpress.net/kinh-doanh"


def scrape_vnexpress_news(pages=7):
    articles = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}-p{page}" if page > 1 else BASE_URL
        print(f"Fetching: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Lấy danh sách bài viết
        for item in soup.select("h3.title-news a"):
            link = item.get("href")
            title = item.get_text(strip=True)
            if not link.startswith("http"):
                continue
            try:
                art_res = requests.get(link)
                art_soup = BeautifulSoup(art_res.content, "html.parser")

                desc_tag = art_soup.select_one("meta[name='description']")
                description = desc_tag.get("content") if desc_tag else ""

                image_tag = art_soup.select_one("meta[property='og:image']")
                image = image_tag.get("content") if image_tag else ""

                content_tag = art_soup.select_one("article.fck_detail")
                content = content_tag.get_text(strip=True) if content_tag else ""

                articles.append({
                    "Tiêu đề": title,
                    "Mô tả": description,
                    "Hình ảnh": image,
                    "Nội dung": content
                })
            except Exception as e:
                print(f"Lỗi khi xử lý bài viết: {link} - {e}")

    # Tạo file lưu trữ
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(articles)
    df.to_csv("data/news_data.csv", index=False, encoding="utf-8-sig")
    print("Đã lưu dữ liệu vào data/news_data.csv")


schedule.every().day.at("06:00").do(scrape_vnexpress_news)

if __name__ == "__main__":
    print("Bắt đầu theo dõi lịch 06:00 mỗi ngày")
    while True:
        schedule.run_pending()
        time.sleep(60)
