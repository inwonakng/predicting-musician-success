#%%

from utils import crawl_db,release_trends,music_graph

import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(title='actions')

parser_crawl = subparsers.add_parser('crawl',
                                    #  parents=[parser],
                                     description='crawl the docker db to gather musicians database',
                                    #  add_help=False,
                                     )
parser_crawl.set_defaults(func=crawl_db)

parser_release = subparsers.add_parser('release',
                                    #    parents=[parser],
                                       description='clean up gathered data to contain us only release',
                                    #    add_help=False
                                       )
parser_release.set_defaults(func=release_trends)
parser_release.add_argument('n_bins',type=int)

parser_graph = subparsers.add_parser('musgraph',
                                     description='Construct graph out of cleaned data')
parser_graph.set_defaults(func=music_graph)
parser_graph.add_argument('n_bins',type=int)


args = vars(parser.parse_args())

operation = args.pop('func')
operation(**args)
# print(parser_release.parse_args())

# operation.func()