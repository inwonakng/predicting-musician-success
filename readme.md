# Analyzing and Predicting Success of Professional Musicians

This repository contains the dataset and some code used to run the analysis from **Analyzing and Predicting Success of Professional Musicians**

The experiments in this project were ran in python. The following packages may be required to run the complete code
```
sklearn
pandas
xgboost
networkx
matplotlib
plotly
tqdm
requests
```

### Raw dataset
The raw data of the musicians graph is availble under [data/musician-graph](data/musician-graph).

A complete collection of the musicians and their releases (with the features) is available under [data/artist_songs](data/artist_songs)

If one wishes, the dataset can be re-collecting using the `python3 main.py crawl`. Due to the nature of the crawler, this process can be re-ran until the crawler doesn't find any more new artists from features to include in the dataset.

In order for this process to work correctly, the Spotify API keys need to be filled in the file [utils/spotify_id.py](utils/spotify_id.py).
The MusicBrainz docker must also be downloaded and be running. In order for the code to find the database on the docker image, the docker-compose.yml must be editted so that the database is exposed in port 5432. The parameter for services/db should be changed as follows. (Note that the only change is in adding the 'expose' argument)
```yaml
services:
  db:
    build:
      context: build/postgres
      args:
        - POSTGRES_VERSION=${POSTGRES_VERSION:-12}
    image: musicbrainz-docker_db:${POSTGRES_VERSION:-12}
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"
    restart: unless-stopped
    command: postgres -c "shared_buffers=2048MB" -c "shared_preload_libraries=pg_amqp.so"
    env_file:
      - ./default/postgres.env
    shm_size: "2GB"
    volumes:
      - pgdata:/var/lib/postgresql/data
    expose:
      - "5432"
    ports:
      - "${MUSICBRAINZ_WEB_SERVER_PORT:-5432}:5432"
```

Once the crawling is finished, then the user must run the `python3 main.py musgraph` command to create a graph of the musicians network. This will produce the `.gml` files under [data/musician-graph](data/musician-graph).

### Using the dataset
The dataset is also availble in code using the custom modules under [utils](utils), by using the `MusicDataLoader` interface.

An example of the usage can be seen in [identify_top.ipynb](identify_top.ipynb). This file trains 3 separate XGBoost trees for each success metric (popularity score, number of followers, appearing on Billboard's Hot 100), and outputs the tree diagram under the [pics](pics) directory. Once these models are trained, it also runs a simulation on creating artificial career profiles of non-successful musicians and tries to bring them to success according to our models by applying random permutations.


Bibtex Citation: 
```
```