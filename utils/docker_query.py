#%%
from pypika import Query, Tables, Table
import psycopg2
import pandas as pd
import os
import numpy as np

conn = psycopg2.connect(host='localhost',dbname='musicbrainz_db', port=5432, user='musicbrainz', password='musicbrainz')
cur = conn.cursor()

# %%

def get_features(id):
    base = f'./data/artist_songs/{id}'
    if not os.path.exists(base): 
        # print('gonna make ')
        os.makedirs(base)
    
    artist,artist_credit_name,release_group,release,release_label,label = Tables('artist','artist_credit_name','release_group','release','release_label','label')

    credits = Query().from_(
                artist_credit_name).select(
                artist_credit_name.artist_credit).where(
                artist_credit_name.artist == id)

    songs = Query().from_(
                        artist_credit_name
                    ).join(
                        credits
                    ).on(
                        artist_credit_name.artist_credit==credits.artist_credit
                    ).left_join(
                        artist
                    ).on(
                        artist.id==artist_credit_name.artist
                    ).left_join(
                        release_group
                    ).on(
                        release_group.artist_credit==credits.artist_credit
                    ).left_join(
                        release
                    ).on(
                        release.release_group == release_group.id
                    ).left_join(
                        release_label
                    ).on(
                        release_label.release == release.id
                    ).left_join(
                        label
                    ).on(
                        label.id == release_label.label
                    ).select(
                        artist.id,
                        artist.name,
                        # artist.gid,
                        artist_credit_name.artist_credit,
                        release_group.id,
                        release_group.name,
                        label.id,
                        label.name
                    ).where(
                        release_group.id.notnull() & artist.id != id)
    
    cur.execute(str(songs))
    val = cur.fetchall()

    features = pd.DataFrame(val,columns=['id','name','credit','songid','song','labelid','label'])
    features.labelid = features.labelid.replace(np.nan,-1).astype(int)
    features.id = features.id.astype(int)
    features.drop_duplicates('songid').reset_index(drop=True)
    return features
# %%
