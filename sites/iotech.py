import argparse
import hashlib
import logging
import pickle
import re
import requests
from bs4 import BeautifulSoup

name = 'iotech'
log  = logging.getLogger(name)

def parse(html, args):
    items = []

    iotech = html.select('.structItem--thread:not(.is-sticky)')
    log.debug(f'iotech {len(iotech)} items')

    for item in iotech:
        id    = item['class'][-2].replace('js-threadListItem-', '')
        a     = item.select('.structItem-title a')[-1]
        link  = 'https://bbs.io-tech.fi' + a['href']
        name  = a.get_text()

        items.append({
            'id'   : id,
            'name' : name,
            'price': 0,
            'link' : link,
        })

    return items

