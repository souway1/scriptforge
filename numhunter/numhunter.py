import json
import sys
import os
from datetime import datetime

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, number_type, PhoneNumberType
except ImportError:
    print("Установи библиотеку: pip install phonenumbers")
    sys.exit(1)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

AUTHOR = "@souvvay"
CHANNEL = "@pythonwave"
STATS_FILE = ".numhunter_stats"

TYPE_NAMES = {
    PhoneNumberType.MOBILE: "Мобильный",
    PhoneNumberType.FIXED_LINE: "Городской",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Мобильный/Городской",
    PhoneNumberType.TOLL_FREE: "Бесплатный",
    PhoneNumberType.PREMIUM_RATE: "Премиум",
    PhoneNumberType.VOIP: "VoIP",
    PhoneNumberType.UNKNOWN: "Неизвестно",
}


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def print_banner():
    clear()
    print(f"""{RED}{BOLD}
  ███╗   ██╗██╗   ██╗███╗   ███╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
  ████╗  ██║██║   ██║████╗ ████║██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
  ██╔██╗ ██║██║   ██║██╔████╔██║███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
  ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
  ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{RESET}{CYAN} OSINT-инструмент для анализа номеров{RESET}

{GREEN} Автор:{RESET}  {AUTHOR}   {GREEN}Канал:{RESET}  {CHANNEL}
""")


def print_menu():
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD} МЕНЮ{RESET}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  {CYAN}[1]{RESET} Проверить номер")
    print(f"  {CYAN}[2]{RESET} Проверить список из файла")
    print(f"  {CYAN}[3]{RESET} Валидация")
    print(f"  {CYAN}[4]{RESET} Статистика")
    print(f"  {CYAN}[0]{RESET} Выход")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def update_stats():
    count = 0
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                count = int(f.read().strip())
        except (ValueError, IOError):
            count = 0
    count += 1
    with open(STATS_FILE, "w") as f:
        f.write(str(count))
    return count


def get_stats():
    if not os.path.exists(STATS_FILE):
        return 0
    try:
        with open(STATS_FILE, "r") as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return 0


def get_number_type(nt):
    return TYPE_NAMES.get(nt, "Неизвестно")


def generate_dorks(phone):
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    return {
        "Google": f"https://www.google.com/search?q=%22{phone}%22",
        "VK": f"https://vk.com/search?c%5Bq%5D={clean}",
        "Telegram": f"https://t.me/{clean}",
        "WhatsApp": f"https://wa.me/{clean}",
        "Facebook": f"https://www.facebook.com/search/top?q={phone}",
    }


def lookup(phone_input):
    try:
        parsed = phonenumbers.parse(phone_input, None)
    except phonenumbers.NumberParseException as e:
        return {"error": str(e)}

    if not phonenumbers.is_valid_number(parsed):
        return {"error": "Номер невалиден"}

    tz_list = timezone.time_zones_for_number(parsed)
    tz = tz_list[0] if tz_list else "Неизвестно"

    return {
        "input": phone_input,
        "formatted": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "country": phonenumbers.region_code_for_number(parsed) or "Неизвестно",
        "region": geocoder.description_for_number(parsed, "ru") or "Неизвестно",
        "operator": carrier.name_for_number(parsed, "ru") or "Неизвестно",
        "type": get_number_type(number_type(parsed)),
        "timezone": tz,
        "dorks": generate_dorks(phone_input),
        "timestamp": datetime.now().isoformat(),
    }


def print_report(data):
    print(f"\n{CYAN}📱 {data['formatted']}{RESET}")
    print(f"  {GREEN}Страна:{RESET}       {data['country']}")
    print(f"  {GREEN}Регион:{RESET}       {data['region']}")
    print(f"  {GREEN}Оператор:{RESET}     {data['operator']}")
    print(f"  {GREEN}Тип:{RESET}          {data['type']}")
    print(f"  {GREEN}Часовой пояс:{RESET} {data['timezone']}")
    print(f"\n{YELLOW}🔍 Ссылки:{RESET}")
    for name, url in data["dorks"].items():
        print(f"  • {name}: {url}")


def save_json(data, phone):
    filename = f"phone_{phone.replace('+', '').replace(' ', '').replace('-', '')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename


def mode_single():
    phone = input(f"\n{CYAN}Номер (например, +79991234567): {RESET}").strip()
    if not phone:
        print(f"{RED}Пусто. Отмена.{RESET}")
        return

    result = lookup(phone)
    if "error" in result:
        print(f"{RED}Ошибка: {result['error']}{RESET}")
        return

    print_report(result)
    filename = save_json(result, phone)
    count = update_stats()
    print(f"\n{GREEN}✓ Отчёт: {filename}{RESET}")
    print(f"{YELLOW}Всего проверок: {count}{RESET}")


def mode_batch():
    path = input(f"\n{CYAN}Путь к файлу (по одному номеру в строке): {RESET}").strip()
    if not os.path.exists(path):
        print(f"{RED}Файл не найден.{RESET}")
        return

    with open(path, "r", encoding="utf-8") as f:
        numbers = [line.strip() for line in f if line.strip()]

    if not numbers:
        print(f"{RED}Файл пуст.{RESET}")
        return

    print(f"\n{YELLOW}Обрабатываю {len(numbers)} номеров...{RESET}\n")
    results = []
    for num in numbers:
        result = lookup(num)
        if "error" in result:
            print(f"{RED}✗ {num} — {result['error']}{RESET}")
        else:
            print(f"{GREEN}✓ {num} — {result['country']} / {result['operator']}{RESET}")
            results.append(result)
        update_stats()

    if results:
        out = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n{GREEN}Сохранено: {out}{RESET}")
    print(f"{YELLOW}Успешно: {len(results)} / {len(numbers)}{RESET}")


def mode_validate():
    phone = input(f"\n{CYAN}Номер для проверки: {RESET}").strip()
    if not phone:
        return
    try:
        parsed = phonenumbers.parse(phone, None)
        valid = phonenumbers.is_valid_number(parsed)
        possible = phonenumbers.is_possible_number(parsed)
        status = f"{GREEN}валиден{RESET}" if valid else f"{RED}невалиден{RESET}"
        poss = f"{GREEN}да{RESET}" if possible else f"{RED}нет{RESET}"
        print(f"\nНомер: {phone}")
        print(f"Валидность:   {status}")
        print(f"Возможность:  {poss}")
    except phonenumbers.NumberParseException as e:
        print(f"{RED}Ошибка: {e}{RESET}")


def mode_stats():
    count = get_stats()
    print(f"\n{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f" {GREEN}Всего проверок:{RESET} {count}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")


def main():
    while True:
        print_banner()
        print_menu()
        choice = input(f"\n{CYAN}Выбор: {RESET}").strip()

        if choice == "1":
            mode_single()
        elif choice == "2":
            mode_batch()
        elif choice == "3":
            mode_validate()
        elif choice == "4":
            mode_stats()
        elif choice == "0":
            print(f"\n{MAGENTA}Больше инструментов — в канале: {CHANNEL}{RESET}\n")
            break
        else:
            print(f"{RED}Неверный пункт.{RESET}")

        if choice != "0":
            input(f"\n{YELLOW}Enter — в меню...{RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{MAGENTA}Прервано. Канал: {CHANNEL}{RESET}\n")
