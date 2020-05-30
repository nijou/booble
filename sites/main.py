import hashlib
import json
import logging
import pickle
import re
import requests
import sys
import unicodedata
from bs4     import BeautifulSoup
from pathlib import Path

from sites import iotech
from sites import murobbs
from sites import tori

log = logging.getLogger('main')


def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKC', value)
    value = value.replace('.', '-')
    value = value.replace('@', '-')
    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
    return re.sub(r'[-\s]+', '-', value)


def login(site, args):
    session      = requests.Session()
    session_name = slugify(f'{site.name}-{args.u}')
    session_file = f'{args.cache_dir}/{session_name}.session'

    try:
        with open(session_file, 'rb') as file:
            session.cookies.update(pickle.load(file))

        log.debug(f'session {session_file} found')
        return session

    except:
        log.debug(f'{session_file} not found attempting login')
        pass

    site.login(session, args.u, args.p)

    with open(session_file, 'wb') as file:
        pickle.dump(session.cookies, file)

    log.debug(f'saved session to {session_file}')

    return session


def fetch(site, url, args):
    http     = login(site, args) if args.u else requests
    response = http.get(url)

    if response.status_code != 200:
        raise EnvironmentError('status code not 200, exit')

    return response.text


def main(url, args):
    name     = re.search(r'(tori|io-tech|murobbs|verkkokauppa)', url, re.I).group(1).replace('-', '')
    site     = globals()[name]
    hash     = hashlib.sha1(url.encode('UTF-8')).hexdigest()[:5]
    filename = f'{args.cache_dir}/{site.name}-previous-run-{hash}.txt'
    dev_file = f'{args.cache_dir}/dev-{site.name}-{hash}.html'

    log.debug(f'url:            "{url}"')
    log.debug(f'name:           "{name}"')
    log.debug(f'hash:           "{hash}"')
    log.debug(f'filename:       "{filename}"')

    # get stuff
    data = ''

    if args.dev:
        try:
            with open(dev_file, 'r') as file:
                data = file.read()
                log.debug(f'using dev file  "{dev_file}""')
        except:
            with open(dev_file, 'w') as file:
                data = fetch(site, url, args)
                file.write(data)
                log.debug(f'new dev data fetched')

    if not data:
        data = fetch(site, url, args)

    # parse stuff
    html  = BeautifulSoup(data, 'html.parser')
    items = site.parse(html, args)

    log.debug('--- all items ---')
    [ log.debug(item) for item in items ]

    # find old stuff
    previous_ids = []

    try:
        with open(filename, 'r') as file:
            previous_ids = file.read().split(',')
            log.debug(f'{len(previous_ids)} previous ids found')
            log.debug('--- look for new items ---')
            if args.dev:
                previous_ids.pop(0)
                previous_ids.pop(0)
                log.debug('dev removed first 2 items from previous ids')

    except:
        log.debug(f'{filename} not found, don\'t look for new items')

    # find new stuff
    if previous_ids:

        notifications = 0
        keep_looking  = 5

        for item in items:
            id    = item['id']
            name  = item['name'][:args.name_length]
            link  = item['link']
            price = item['price']

            if id in previous_ids:
                log.debug(f'[familiar item {keep_looking}] {id} -> {name}')
                keep_looking -= 1

                if keep_looking:
                    continue

                log.debug(f'stop looking')
                break

            if args.filter and not eval(args.filter):
                log.debug('--- filter did not match ---')
                log.debug(f'filter {args.filter}')
                log.debug(item)
                continue

            if not args.format or args.format == 'json':
                print(json.dumps(item))
                continue

            notifications += 1

            print(args.format.format(
                id    = id,
                price = str(price)[:args.price_length],
                name  = name,
                link  = link
            ))

        sys.stdout.flush()

    # remember these ids for next time
    ids = [ item['id'] for item in items ]
    ids = ','.join(ids).rstrip()

    with open(filename, 'w') as file:
        file.write(ids)


