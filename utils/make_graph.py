import pandas as pd
import networkx as nx
import numpy as np
from tqdm.auto import tqdm
import os
from collections import Counter

def musicians(n_bins):
    base = f'./data/musician-graph'
    if os.path.exists(f'{base}/graph_{n_bins}.gml'): return
    
    print('reading in data...')
    
    nodes = pd.read_csv(f'{base}/nodes_{n_bins}.csv')
    edges = pd.read_csv(f'{base}/edges_{n_bins}.csv')

    G = nx.DiGraph()
    pair_counts = [(n1,n2,int(w))
                        for n1, feats in edges.groupby('name_1')
                    for n2,w in Counter(feats.name_2.values).items()]    
    # for n1, feats in edges.groupby('name_1'):
    #     print(n1)
    #     print(feats)
    #     for n2,w in Counter(feats.name_2.values).items():
    #         print()
    # return
    G.add_nodes_from(nodes.name)
    G.add_weighted_edges_from(pair_counts)
    # G.add_edges_from([[a1,a2]for id1,a1,id2,a2,sid,s in tqdm(edges.values,desc='adding edges to graph..')])


    # add extra features from spotify!
    for feature in ['popularity','followers','genres']:    
        if nodes[feature].dtype == float:
            nodes[feature] = nodes[feature].replace(np.nan,0)
        vals = dict(nodes[['name',feature]].values)
        nx.set_node_attributes(G,vals,feature)

    # print('adding betweenness..')
    # bc = nx.betweenness_centrality(G,normalized=True,endpoints=True)
    # nx.set_node_attributes(G,bc,'betweenness')

    print('adding eigenvector..')
    ec = nx.eigenvector_centrality(G)
    nx.set_node_attributes(G,ec,'eigenvector')

    nx.write_gml(G,f'{base}/graph_{n_bins}.gml')
#     nx.write_gexf(G,f'{base}/test.gexf')

def labels(prefix=''):
    if prefix: prefix += '_'
    print('reading in data...')
    base = f'./data/label-graph'
    if os.path.exists(f'{base}/graph.gml'): return
    
    nodes = pd.read_csv(f'{base}/nodes.csv')
    edges = pd.read_csv(f'{base}/edges.csv')

    G = nx.Graph()
    G.add_edges_from([[n1,n2]for n1,n2 in tqdm(edges[['name_1','name_2']].values,desc='adding edges to graph..')])

    # add extra features from spotify!
    for feature in edges.columns[edges.columns.str.contains('artist')]:    
        if edges[feature].dtype == float:
            edges[feature] = edges[feature].replace(np.nan,0)
        vals = dict(zip(edges[['name_1','name_2']].to_records(index=False).tolist(),edges[feature].values))

        nx.set_edge_attributes(G,vals,feature)
        
    # .... TODO!