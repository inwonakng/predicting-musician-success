# %%
import pandas as pd
from utils.get_release import get_release
from tqdm.auto import tqdm
import os

'''
## Loading data

At this step, we grab the US releases of each artist in the dataset. Since not all artists had releases in the US, we can also use this to narrow down our musicians list
'''

# %%

def get_release_trends(n_bins):
    if any(not os.path.exists(f) for f in [
        f'data/musician-graph/nodes_{n_bins}.csv',
        f'data/musician-graph/edges_{n_bins}.csv',
        f'data/musician-graph/release_{n_bins}.csv'
    ]):
    
        mus_nodes = pd.read_csv('data/musician-graph/raw_nodes.json')
        mus_edges = pd.read_csv('data/musician-graph/raw_edges.json')
        dat = get_release(mus_nodes.id.values)
        release_dat = dat[dat.artist.isin(mus_nodes.id) & (dat.artist!=1)]
        us_mus_nodes = mus_nodes[mus_nodes.id.isin(release_dat.artist)]
        us_mus_edges = mus_edges[mus_edges.id_1.isin(us_mus_nodes.id) & mus_edges.id_2.isin(us_mus_nodes.id)]

        release_trends = []

        for a,songs in tqdm(release_dat.groupby('artist'),desc='gathering releases for artists..'):
            stamped = songs[~songs.release_date.isnull()]

            by_stamp = stamped.sort_values('release_date')
            by_stamp =by_stamp[by_stamp.release_date < pd.Timestamp('2021')]

            start = by_stamp.release_date.min()
            end = by_stamp.release_date.max()
            career_span = end- start
            c_bin = career_span//n_bins

            binned = [by_stamp[(by_stamp.release_date >= start+c_bin*i) & (by_stamp.release_date < start+c_bin*(i+1))]
                for i in range(n_bins-1)
            ]+[
                by_stamp[by_stamp.release_date >= start+c_bin*n_bins]
            ]
            num_release = [len(b) for b in binned]
            release_trends.append({'id':a,
                                    'histogram':[sum(num_release[:i]) for i in range(n_bins)],
                                    'num_release': sum(num_release),
                                    'first_release':by_stamp.release_date.min(),
                                    'last_release':by_stamp.release_date.max()})

        release_trends = pd.DataFrame(release_trends)

        us_mus_nodes = us_mus_nodes.merge(release_trends,on=['id'])
        us_mus_nodes = us_mus_nodes[(~us_mus_nodes.followers.isnull()) & (~us_mus_nodes.popularity.isnull())]
        us_mus_nodes.to_csv(f'data/musician-graph/nodes_{n_bins}.csv',index=False)
        us_mus_edges.to_csv(f'data/musician-graph/edges_{n_bins}.csv',index=False)
        release_dat.to_csv(f'data/musician-graph/release_{n_bins}.csv',index=False)
