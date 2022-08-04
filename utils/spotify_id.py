#%%
from pypika import Query, Tables, Table
import psycopg2
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

#%%

# spotify key
API_AUTH='https://accounts.spotify.com/api/token'
Q_ARTISTS='https://api.spotify.com/v1/artists'
Q_ALBUMS='https://api.spotify.com/v1/albums'
CLIENT_ID='TO_BE_FILLED'
CLIENT_SECRET='TO_BE_FILLED'
response = session.post(API_AUTH, 
                            data={'grant_type':'client_credentials'}, 
                            auth = (CLIENT_ID, CLIENT_SECRET)) 

token_raw = json.loads(response.text)
token = token_raw["access_token"]
HEADER={'Authorization':f'Bearer {token}','Content-Type': 'application/json'}


conn = psycopg2.connect(host='localhost',dbname='musicbrainz_db', port=5432, user='musicbrainz', password='musicbrainz')
cur = conn.cursor()
artist,l_artist_url,url = Tables('artist','l_artist_url','url')


#%%
def get_spotify_id(ids):
            # getting spotify id
    query = Query().from_(
                l_artist_url).join(
                artist).on(l_artist_url.entity0==artist.id).join(
                url).on(l_artist_url.entity1==url.id).where(
                artist.id.isin(ids.id.values.tolist())).select(
                artist.id, url.url)

    cur.execute(str(query))
    urls = pd.DataFrame(cur.fetchall(),columns=['id','url'])

    spo_ids = {}
    for id,data in tqdm(urls.groupby('id'),desc='going by artist...'):
        spotify = [r for r in data.url.values if 'spotify' in r and 'artist/' in r]
        if spotify:
            spo_ids[id] = spotify[0].split('artist/')[1]

    ids['spotifyid'] = ids.id.apply(lambda x: spo_ids[x] if x in spo_ids else np.nan)
    return ids


def get_spotify_data(ids):
    
    valid = ids[~ids.spotifyid.isnull()]
    valid.reset_index(drop=True,inplace=True)
    spoids = valid.spotifyid.values
    # split into 50 ids
    chunks = np.array_split(spoids,np.ceil(len(spoids)/50))

    # now we have spotify access token
    total = []
    for c in tqdm(chunks,desc='sending to spotify in chunks..'):
        s = ','.join(c)
        r = session.get(url=f'{Q_ARTISTS}?ids={s}',headers=HEADER)
        total+=json.loads(r.content)['artists']
        
    total = pd.json_normalize(total)
    ret = pd.concat([valid,total[['genres','popularity','followers.total']]],axis=1)
    # ret = pd.concat([before,ret])
    # ret.to_csv(f'./data/SPO_round{round_i}.csv',index=False)
    return ret

# %%
# ids = pd.read_csv('./data/fromtop1000/SPO_round14.csv')
# sample = ids.spotifyid.values[0]
# r = session.get(url=f'{Q_ARTISTS}/{sample}/albums',headers=HEADER)
# dat = json.loads(r.content)
# albums = pd.json_normalize(dat['items']).id.values
# r = session.get(url=f'{Q_ALBUMS}?ids={",".join(albums)}',headers=HEADER)
# %%
