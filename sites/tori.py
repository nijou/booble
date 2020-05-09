import argparse
import hashlib
import logging
import pickle
import re
import requests
from bs4 import BeautifulSoup

name = 'tori'
log  = logging.getLogger(name)

def login(session, user, password):
    return session.post('https://www.tori.fi/tili/do_login', {
        'orig_uri'   : 'tili',
        'email'      : user,
        'password'   : password,
        'has_account': 'yes',
    })


def parse(html, args):
    if html.html['id'] == 'mypages':
        return _parse_logged_in(html, args)

    return _parse_public(html, args)


# tori.fi hakuvahti
def _parse_logged_in(html, args):
    items = []

    tori = html.select('.item_row')
    log.debug(f'tori logged_in {len(tori)} items')

    for item in tori:
        a = item.select_one('.item_link')

        if not a:
            name = item.select_one('.gray_text').get_text()
            name = re.sub(r'\s+', ' ', name)
            log.debug(f'{name} sold / removed, skip')
            continue

        id    = item['id'].replace('item_', '')
        link  = a['href']
        name  = a.get_text()
        price = item.select_one('.list_price').get_text()

        name  = re.sub(r'\s+', ' ', name)
        price = int(re.sub(r'\D', '', price) or 0)

        items.append({
            'id'   : id,
            'name' : name,
            'price': price,
            'link' : link,
        })

    return items


# tori.fi julkinen hakutulos
def _parse_public(html, args):
    items = []

    tori  = html.select('a.item_row_flex')
    log.debug(f'tori public {len(tori)} items')

    for item in tori:
        id    = item['id'].replace('item_', '')
        link  = item['href']
        price = item.select_one('.list_price').get_text()
        name  = item.select_one('.li-title')  .get_text()

        name  = re.sub(r'\s+', ' ', name)
        price = int(re.sub(r'\D', '', price) or 0)

        items.append({
            'id'   : id,
            'name' : name,
            'price': price,
            'link' : link,
        })

    return items

