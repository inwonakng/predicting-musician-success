from sklearn.metrics import confusion_matrix,f1_score
import pandas as pd

def test(model,X_train,X_test,y_train,y_test,verbose=True):
    if verbose:
        print('================')
        print(type(model))

    model.fit(X_train,y_train)
    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)
    if verbose: 
        print(f'training acc: {(y_train == pred_train).sum() / len(y_train)}')
        print(f'training F1: {f1_score(y_train,pred_train)}')
        print(confusion_matrix(y_train,pred_train))
        
        print(f'testing acc: {(y_test == pred_test).sum() / len(y_test)}')
        print(f'testing F1: {f1_score(y_test,pred_test)}')
        print(confusion_matrix(y_test,pred_test))
    return f1_score(y_test,pred_test)

# iterative approach. instead of using network as input, let's first see if we can divide the network into nodes and then do it.
# lets featurize the dataset first
def featurize_mus(
        mus_nodes,
        target = 'popularity',
        thresh=50, 
        exclude_features = [],
        extra_features = []
    ):
    scalar_features = ['followers', 'popularity', 'network_rank','in_edges','out_edges','num_release'] + extra_features
    scalar_features = [f for f in scalar_features if not f in exclude_features]
    scalar_features = list(filter(lambda x: x!=target, scalar_features))
    # first get all genres and create a base mask
    # allgenres = list(set([g for gg in mus_nodes.genres.values.tolist() for g in gg]))
    # get_genre_mask = lambda glist: [int(g in glist) for g in allgenres]

    
    features=pd.DataFrame()
    features[scalar_features] = mus_nodes[scalar_features]

    firsts = pd.to_datetime(mus_nodes.first_release)
    lasts = pd.to_datetime(mus_nodes.last_release)
    # drop artists with invalid dates
    
    
    features['first_release'] = firsts.view(int)
    features['last_release'] = lasts.view(int)
    features['career_length'] = (lasts-firsts).view(int)

    # (lasts-firsts).astype(int)
    # features.career_length *= (features.career_length > 0)
    
    features = features[list(set(features.columns)-set(exclude_features))]
    
    return (mus_nodes[target].values >= thresh).astype(int),features