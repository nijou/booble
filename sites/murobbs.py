import argparse
import hashlib
import logging
import pickle
import re
import requests
from bs4 import BeautifulSoup

name = 'murobbs'
log  = logging.getLogger(name)

def parse(html, args):
    items = []

    murobbs = html.select('.discussionListItem:not(.sticky)')
    log.debug(f'murobbs {len(murobbs)} items')

    for item in murobbs:
        id    = item['id'].replace('thread-', '')
        a     = item.select('.title a')[-1]
        link  = 'https://murobbs.muropaketti.com/' + a['href']
        name  = a.get_text()

        items.append({
            'id'   : id,
            'name' : name,
            'price': 0,
            'link' : link,
        })

    return items

