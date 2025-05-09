import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import schedule

BASE_URL = "https://vnexpress.net/kinh-doanh"


def scrape_vnexpress_news(pages=5):
    articles = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}-p{page}" if page > 1 else BASE_URL
        print(f"Fetching: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        for item in soup.select(".titem a.title"):
            link = item.get("href")
            title = item.get_text(strip=True)
            if not link.startswith("http"):
                continue
            try:
                art_res = requests.get(link)
                art_soup = BeautifulSoup(art_res.content, "html.parser")
                description = art_soup.select_one("meta[name='description']")
                description = description.get("content") if description else ""
                image_tag = art_soup.select_one("meta[property='og:image']")
                image = image_tag.get("content") if image_tag else ""
                content_tag = art_soup.select_one(".article-content")
                content = content_tag.get_text(strip=True) if content_tag else ""

                articles.append({
                    "Tiêu đề": title,
                    "Mô tả": description,
                    "Hình ảnh": image,
                    "Nội dung": content
                })
            except Exception as e:
                print(f"Lỗi khi xử lý bài viết: {link} - {e}")

    df = pd.DataFrame(articles)
    df.to_csv("data/news_data.csv", index=False, encoding="utf-8-sig")
    print("Đã lưu dữ liệu vào data/news_data.csv")


# Lên lịch chạy lúc 6h sáng hằng ngày
schedule.every().day.at("06:00").do(scrape_vnexpress_news)

if __name__ == "__main__":
    print("Bắt đầu theo dõi lịch...")
    while True:
        schedule.run_pending()
        time.sleep(60)
