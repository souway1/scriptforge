                              checker.py
import asyncio
import aiohttp
import json
from datetime import datetime

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SITES = {
    # ===== РАЗРАБОТКА (15) =====
    "GitHub": "https://github.com/{username}",
    "GitLab": "https://gitlab.com/{username}",
    "Codeberg": "https://codeberg.org/{username}",
    "Gitea": "https://gitea.com/{username}",                                                                                                        "Replit": "https://replit.com/@{username}",
    "HackerNews": "https://news.ycombinator.com/user?id={username}",                                                                                "StackOverflow": "https://stackoverflow.com/users/{username}",
    "Bitbucket": "https://bitbucket.org/{username}/",
    "SourceForge": "https://sourceforge.net/u/{username}/profile",
    "Pypi": "https://pypi.org/user/{username}/",
    "NPM": "https://www.npmjs.com/~{username}",
    "Kaggle": "https://www.kaggle.com/{username}",
    "Keybase": "https://keybase.io/{username}",
    "Gravatar": "https://gravatar.com/{username}",
    "Launchpad": "https://launchpad.net/~{username}",

    # ===== СОЦСЕТИ (10) =====
    "Reddit": "https://www.reddit.com/user/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Instagram": "https://www.instagram.com/{username}/",
    "Minds": "https://www.minds.com/{username}",
    "Vero": "https://vero.co/{username}",
    "Ok": "https://ok.ru/{username}",
    "LiveJournal": "https://{username}.livejournal.com",
    "Diary": "https://{username}.diary.ru",                                                                                                         "Dreamwidth": "https://{username}.dreamwidth.org",
    "Mastodon": "https://mastodon.social/@{username}",

    # ===== ИГРЫ (10) =====
    "Steam": "https://steamcommunity.com/id/{username}",
    "Twitch": "https://www.twitch.tv/{username}",
    "Chess": "https://www.chess.com/member/{username}",
    "Lichess": "https://lichess.org/@/{username}",
    "Faceit": "https://www.faceit.com/en/players/{username}",
    "Osu": "https://osu.ppy.sh/users/{username}",
    "Speedrun": "https://www.speedrun.com/user/{username}",
    "Roblox": "https://www.roblox.com/user.aspx?username={username}",
    "Xbox": "https://xboxgamertag.com/search/{username}",
    "PSN": "https://psnprofiles.com/{username}",

    # ===== МУЗЫКА И ВИДЕО (10) =====
    "SoundCloud": "https://soundcloud.com/{username}",
    "Spotify": "https://open.spotify.com/user/{username}",
    "Bandcamp": "https://{username}.bandcamp.com",
    "Mixcloud": "https://www.mixcloud.com/{username}/",
    "Audiomack": "https://audiomack.com/{username}",
    "ReverbNation": "https://www.reverbnation.com/{username}",
    "Dailymotion": "https://www.dailymotion.com/{username}",
    "Vimeo": "https://vimeo.com/{username}",
    "LastFM": "https://www.last.fm/user/{username}",
    "Discogs": "https://www.discogs.com/user/{username}",

    # ===== ДИЗАЙН И ФОТО (10) =====
    "Flickr": "https://www.flickr.com/people/{username}",
    "Behance": "https://www.behance.net/{username}",
    "Dribbble": "https://dribbble.com/{username}",
    "DeviantArt": "https://www.deviantart.com/{username}",
    "ArtStation": "https://www.artstation.com/{username}",
    "500px": "https://500px.com/p/{username}",
    "Unsplash": "https://unsplash.com/@{username}",
    "Pexels": "https://www.pexels.com/@{username}",
    "Pixabay": "https://pixabay.com/users/{username}/",
    "Figma": "https://www.figma.com/@{username}",

    # ===== БЛОГИ И КОНТЕНТ (10) =====
    "Tumblr": "https://{username}.tumblr.com",
    "Goodreads": "https://www.goodreads.com/{username}",
    "Wattpad": "https://www.wattpad.com/user/{username}",
    "Quora": "https://www.quora.com/profile/{username}",
    "Letterboxd": "https://letterboxd.com/{username}/",
    "Disqus": "https://disqus.com/by/{username}/",
    "Medium": "https://medium.com/@{username}",
    "Substack": "https://{username}.substack.com",
    "WordPress": "https://{username}.wordpress.com",
    "Blogger": "https://{username}.blogspot.com",

    # ===== ОБРАЗОВАНИЕ (8) =====
    "Duolingo": "https://www.duolingo.com/profile/{username}",
    "Coursera": "https://www.coursera.org/user/{username}",
    "Stepik": "https://stepik.org/users/{username}",
    "Habr": "https://habr.com/ru/users/{username}/",
    "Pikabu": "https://pikabu.ru/@{username}",
    "MyAnimeList": "https://myanimelist.net/profile/{username}",
    "AniList": "https://anilist.co/user/{username}/",
    "Trakt": "https://trakt.tv/users/{username}",

    # ===== КРИПТА И ФИНАНСЫ (6) =====
    "CoinMarketCap": "https://coinmarketcap.com/community/profile/{username}/",
    "Binance": "https://www.binance.com/en/profile/{username}",
    "OpenSea": "https://opensea.io/{username}",
    "Rarible": "https://rarible.com/{username}",
    "Ebay": "https://www.ebay.com/usr/{username}",
    "PayPal": "https://www.paypal.me/{username}",

    # ===== СПОРТ И ЗДОРОВЬЕ (4) =====
    "Strava": "https://www.strava.com/athletes/{username}",
    "MyFitnessPal": "https://www.myfitnesspal.com/profile/{username}",
    "NikeRunClub": "https://www.nike.com/member/{username}",
    "Garmin": "https://connect.garmin.com/modern/profile/{username}",

    # ===== ПРОЧЕЕ (8) =====
    "Fiverr": "https://www.fiverr.com/{username}",
    "Notion": "https://{username}.notion.site",
    "Carrd": "https://{username}.carrd.co",
    "Gitbook": "https://{username}.gitbook.io",
    "Surge": "https://{username}.surge.sh",
    "Glitch": "https://{username}.glitch.me",
    "Airbnb": "https://www.airbnb.com/users/show/{username}",
    "TripAdvisor": "https://www.tripadvisor.com/members/{username}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT = aiohttp.ClientTimeout(total=20)
RETRIES = 2

async def check_site(session, name, url):
    for attempt in range(RETRIES):
        try:
            async with session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True) as resp:
                if resp.status == 200:
                    return (name, url, "found")
                elif resp.status == 404:
                    return (name, url, "not_found")
