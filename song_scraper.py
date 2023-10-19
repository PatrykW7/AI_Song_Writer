import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from unidecode import unidecode


def song_scraper(artists: list):
    """
    Scrape song lyrics and their translations from www.tekstowo.pl for a list of artists.

    Args:
        artists (list): A list of artist names for which you want to scrape song lyrics and translations.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped song lyrics and their translations. The DataFrame has two columns: "Polish" and "English"
    """
    dfs = []
    df_text = pd.DataFrame(
        data={"Author": [], "Title": [], "Polish": [], "English": []}
    )

    base_url = "https://www.tekstowo.pl"

    for artist in artists:
        artist_unidecoded = unidecode(artist.replace(" ", "_").lower())
        artist_url = f"https://www.tekstowo.pl/piosenki_artysty,{artist_unidecoded},alfabetycznie,strona,1.html"

        artist_page = requests.get(artist_url)
        soup = BeautifulSoup(artist_page.text, "lxml")

        try:
            max_num_page = soup.find_all("a", class_="page-link")[-2].text
            max_num_page = int(max_num_page)

        except:
            max_num_page = 1

        for num_page in range(1, max_num_page + 1):
            boxes = soup.find_all("div", class_="flex-group")
            songs_urls = {"Url": []}

            for box in boxes:
                try:
                    url = box.find("a", class_="title").get("href")
                    song_url = base_url + url

                    songs_urls["Url"].append(song_url)
                except:
                    pass

            df = pd.DataFrame(songs_urls)
            dfs.append(df)

            next_number_page = num_page + 1
            next_page = f"https://www.tekstowo.pl/piosenki_artysty,{artist_unidecoded},alfabetycznie,strona,{next_number_page}.html"

            page = requests.get(next_page)
            soup = BeautifulSoup(page.text, "lxml")

    df_songs = pd.concat(dfs, ignore_index=True)

    for _, row in df_songs.iterrows():
        try:
            song_page = requests.get(row[0])

            soup = BeautifulSoup(song_page.text, "lxml")

            original = soup.find_all("div", class_="inner-text")[0].text
            translated = soup.find_all("div", class_="inner-text")[1].text
            translated = np.nan if translated == "" else translated
            song_title = (
                re.findall(r",[^,]+,([^\.]+)\.", row[0])[0]
                .replace("_", " ")
                .strip()
                .title()
            )

            if re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", original):
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {
                                "Author": artist,
                                "Title": song_title,
                                "Polish": [original],
                                "English": [translated],
                            }
                        ),
                    ],
                    ignore_index=True,
                )

            else:
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {
                                "Author": artist,
                                "Title": song_title,
                                "Polish": [translated],
                                "English": [original],
                            }
                        ),
                    ],
                    ignore_index=True,
                )
        except:
            print(f"Unable to download lyrics from {row[0]}")

    return df_text
