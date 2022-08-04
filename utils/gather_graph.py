
import pandas as pd
from tqdm.auto import tqdm
from itertools import combinations
import os

FEATURES = ['genres','popularity','followers']


def construct(
    final_file,
    music_graph_dir,
    label_graph_dir
):
    mus_nodes = pd.read_csv(final_file)
    
    if any([not os.path.exists(f) for f in [
        f'{music_graph_dir}/raw_nodes.json',
        f'{music_graph_dir}/raw_edges.json',
        # f'{label_graph_dir}/raw_nodes.json',
        # f'{label_graph_dir}/raw_edges.json',
    ]]):
        label_info,label_relations = construct_music(mus_nodes,music_graph_dir)
        # construct_labels(label_info,label_relations, label_graph_dir)

    
    
def construct_music(mus_nodes,music_graph_dir):
    mus_edges = []
    label_info = []
    # features to save along with artist info

    for vals in tqdm(mus_nodes[['id','name']+FEATURES].values,desc='making song network...'):
        a_id,a_name = vals[:2]
        features = vals[2:]
        f = pd.read_csv(f'./data/artist_songs/{a_id}/features.csv')
        f['owner_id'] = a_id
        f['owner_name'] = a_name
        label_relations = f[['owner_id','owner_name','labelid','label']]
        label_relations = label_relations[(~label_relations.label.isnull()) & (label_relations.label!='[no label]')]
        label_relations[FEATURES] = features
        label_info += label_relations.values.tolist()
        mus_edges+= f[['owner_id','owner_name','id','name','songid','song']].values.tolist()
        
    mus_edges = pd.DataFrame(mus_edges,columns=['id_1','name_1','id_2','name_2','songid','song']).drop_duplicates()
    mus_edges.reset_index(drop=True,inplace=True)

    label_info = pd.DataFrame(label_info,
                    columns=['id','name','labelid','label']+FEATURES).drop_duplicates()
    label_info.reset_index(drop=True,inplace=True)

    if not os.path.exists(music_graph_dir): 
        os.mkdir(music_graph_dir)
    mus_nodes.to_csv(f'{music_graph_dir}/raw_nodes.json',index=False)
    mus_edges.to_csv(f'{music_graph_dir}/raw_edges.json',index=False)
    
    return label_info,label_relations
    
    
def construct_labels(label_info,label_relations,label_graph_dir):
    label_nodes = label_info[['labelid','label']].drop_duplicates()
    label_nodes.reset_index(drop=True,inplace=True)
    label_edges = []

    for (aid,aname),data in tqdm(label_info.groupby(['id','name']),desc='making label network...'): 
        if aid == 1: continue
        artist_features = data[FEATURES].values[0].tolist()
        for (lid1,lname1),(lid2,lname2) in combinations(data[['labelid','label']].values,2):
            label_edges.append([lid1,lname1,lid2,lname2,aid,aname]+artist_features)

    label_edges = pd.DataFrame(label_edges,
                            columns=['id_1',
                                        'name_1',
                                        'id_2',
                                        'name_2',
                                        'artistid',
                                        'artist']+[f'artist_{f}' for f in FEATURES])

    if not os.path.exists(label_graph_dir): 
        os.mkdir(label_graph_dir)
    label_nodes.to_csv(f'{label_graph_dir}/raw_nodes.json',index=False)
    label_edges.to_csv(f'{label_graph_dir}/raw_edges.json',index=False)