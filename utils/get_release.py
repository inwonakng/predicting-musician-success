#%%
from pypika import Query, Tables
import psycopg2
import pandas as pd
from tqdm import tqdm

conn = psycopg2.connect(host='localhost',dbname='musicbrainz_db', port=5432, user='musicbrainz', password='musicbrainz')
cur = conn.cursor()
# artist_id = 600808
tag,release_group_tag = Tables('tag','release_group_tag')

def get_release(artist_ids):
    release,release_country,artist_credit,artist_credit_name = Tables('release','release_country','artist_credit','artist_credit_name')

    songs = Query().from_(
                    release
                ).join(
                    release_country
                ).on(
                    release_country.release == release.id
                ).join(
                    artist_credit
                ).on(
                    release.artist_credit == artist_credit.id
                ).join(
                    artist_credit_name
                ).on(
                    artist_credit_name.artist_credit == artist_credit.id
                ).select(
                    artist_credit_name.artist,
                    release.id,
                    release.name,
                    release_country.date_year,
                    release_country.date_month,
                    release_country.date_day,
                ).where(
                    artist_credit_name.artist.isin(artist_ids) and release_country.country == 222
                )


    cur.execute(str(songs))
    val = cur.fetchall()

    df = pd.DataFrame(val,columns=['artist','song_id','song_name','year','month','day'])
    df[['month','day']] = df[['month','day']].fillna(1)
    df['release_date'] = pd.to_datetime(df[['year','month','day']])
    return df[['artist','song_id','song_name','release_date']]

