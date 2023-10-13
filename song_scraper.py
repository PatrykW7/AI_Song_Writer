import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np


def song_scraper(artists: list):
    """
    Scrape song lyrics and their translations from www.tekstowo.pl for a list of artists.

    Args:
        artists (list): A list of artist names for which you want to scrape song lyrics and translations.

    Returns:
        pd.DataFrame: A DataFrame containing the scraped song lyrics and their translations. The DataFrame has two columns: "Original" and "Translated."
    """
    dfs = []
    df_text = pd.DataFrame(data={"Original": [], "Translated": []})

    base_url = "https://www.tekstowo.pl"

    for i in artists:
        artist_url = (
            f"https://www.tekstowo.pl/piosenki_artysty,{i},alfabetycznie,strona,1.html"
        )

        artist_page = requests.get(artist_url)
        soup = BeautifulSoup(artist_page.text, "lxml")

        max_num_page = soup.find_all("a", class_="page-link")[-2].text
        max_num_page = int(max_num_page)

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
            next_page = f"https://www.tekstowo.pl/piosenki_artysty,{i},alfabetycznie,strona,{next_number_page}.html"

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

            if re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", original):
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {"Original": [original], "Translated": [translated]}
                        ),
                    ],
                    ignore_index=True,
                )

            else:
                df_text = pd.concat(
                    [
                        df_text,
                        pd.DataFrame(
                            {"Original": [translated], "Translated": [original]}
                        ),
                    ],
                    ignore_index=True,
                )
        except:
            pass

    return df_text
