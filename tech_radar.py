import feedparser
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

def get_github_trending():
    url = "https://github.com/trending"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    repos = []

    for repo in soup.find_all("h2"):
        name = repo.text.strip()
        repos.append(name)

    return repos


def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    OPENAI_KEY = os.getenv("OPENAI_KEY")

    client = OpenAI(api_key=OPENAI_KEY)

    feeds = [
        "https://venturebeat.com/category/ai/feed/",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "https://tldr.tech/ai/rss"
    ]

    news = []

    for feed in feeds:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries:
            news.append(entry.title)


    github_projects = get_github_trending()

    news_text = "\n".join(news)
    github_text = "\n".join(github_projects)

    prompt = f"""
    Select most important items from this list.
    Explain briefly why they matter.

    News:
    {news_text}

    GitHub:
    {github_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response.choices[0].message.content

    message = f"🧠 AI Tech Radar\n\n{summary}"

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message}
    )

 
if __name__ == "__main__":
    main()