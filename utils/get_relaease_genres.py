#%%
from pypika import Query, Tables
import psycopg2
import pandas as pd

conn = psycopg2.connect(host='localhost',dbname='musicbrainz_db', port=5432, user='musicbrainz', password='musicbrainz')
cur = conn.cursor()

tag,release_group_tag = Tables('tag','release_group_tag')
def get_release_genres(release_id):
    genres = Query().from_(
        release_group_tag
    ).join(
        tag
    ).on(
        tag.id == release_group_tag.tag    
    ).select(
        tag.name,
        tag.id,
        release_group_tag.count,
    ).where(
        release_group_tag.release_group == release_id
    )
    
    cur.execute(str(genres))
    val = cur.fetchall()

    return pd.DataFrame(val,columns=['genre_name','genre_id','genre_count'])
    
# %%
