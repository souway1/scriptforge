import requests
from bs4 import BeautifulSoup

url = input("Введи ссылку: ")

try:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            print("Заголовок:", soup.title.text.strip())
        else:
            print("Заголовок не найден")

        print("\nСсылки:")
        for link in soup.find_all("a")[:5]:
            print("—", link.text.strip())
    else:
        print("Ошибка:", response.status_code)
except Exception as e:
    print("Не удалось подключиться:", e)
