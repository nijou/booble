#!/usr/bin/env python3

import argparse
import fileinput
import logging
import os
import select
import sys
from pathlib import Path

from sites.main import main

log = logging.getLogger('booble')

if __name__ == "__main__":

    example_url = 'https://www.tori.fi/koko_suomi?q=tietokone&cg=0&w=3&xtatc=INT-166'

    cli = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description =
            '\nFind if new items have been posted since the last run'
            '\n'
            '\nExamples:'
            '\n'
            '\n'+__file__+'                             ' +example_url+
            '\n'+__file__+' --format "{name}"           ' +example_url+
            '\n'+__file__+' --format "{price} - {name}" ' +example_url+
            '\n'+__file__+' --name-length 42            ' +example_url+
            '\n'
            '\necho "'+example_url+'" | '+__file__+' --filter "price < 420"'
            '\n'
            '\nSupports:'
            '\n - tori.fi'
            '\n - bbs.io-tech.fi'
            '\n - murobbs.muropaketti.com'
    )

    cli.add_argument('url', nargs='*', help = 'Url to the list of posts\n\n')

    cli.add_argument('-v',    action  = 'store_true', help = 'debug logging\n\n')
    cli.add_argument('--dev', action  = 'store_true', help = 'Only fetch url if no data on disk. Cache response to disk and use it on subsequent runs.\n\n')
    cli.add_argument('-u',    metavar = 'user',       help = 'Username\n\n')
    cli.add_argument('-p',    metavar = 'pass',       help = 'Password\n\n')

    cli.add_argument('--cache-dir', metavar = '~/.cache/booble', help = 'Where to store previous runs and session files\n\n')

    cli.add_argument('--name-length', type = int, default = 40, metavar = '40',
        help = 'Static length for item name in output\n\n')

    cli.add_argument('--price-length', type = int, default = 8, metavar = '8',
        help = 'Static length for item price in output\n\n')

    cli.add_argument('--format',
        default =  '{id} {price:>price-length} {name:<name-length} {link}',
        metavar = '"{id} {price:>price-length} {name:<name-length} {link}"',
        help    = '\nOutput format for an item. Defaults to json'
                  '\n'
                  '\nPython String format'
                  '\nAvailable variables:'
                  '\n - [string] id'
                  '\n - [string] name'
                  '\n - [string] link'
                  '\n - [int]    price'
                  '\n - [int]    name-length'
                  '\n - [int]    price-length '
                  '\n\nhttps://www.w3schools.com/python/ref_string_format.asp\n\n')

    cli.add_argument('--filter',
        metavar = '"price > 50 and price < 100"',
        help    = '\nFilter results with python expression.\n'
                  '\nAvailable variables:'
                  '\n - [string] id'
                  '\n - [string] name'
                  '\n - [string] link'
                  '\n - [int]    price\n\n')


    args = cli.parse_args()

    try:
        args.cache_dir = Path(args.cache_dir)
    except:
        here = os.path.dirname(os.path.realpath(__file__))
        args.cache_dir = Path(f'{here}/cache')

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    if args.v:
        logging.basicConfig(
            format  = '%(asctime)s %(levelname)-7s %(name)-14s %(message)s',
            datefmt = '%Y-%m-%d %H:%M:%S',
            level   = logging.DEBUG
        )

    args.format = args.format \
        .replace('name-length',  str(args.name_length)) \
        .replace('price-length', str(args.price_length))

    log.debug(f'user:           "{args.u if args.u else ""}"')
    log.debug(f'pass:           "{"yes"  if args.p else ""}"')
    log.debug(f'name_length:    "{args.name_length}"')
    log.debug(f'price_length:   "{args.price_length}"')
    log.debug(f'format:         "{args.format if args.format else "json"}"')

    n = 0

    if select.select([sys.stdin,], [], [], 0.0)[0]:
        for url in sys.stdin:
            n += 1
            url = url.rstrip()
            log.debug(f'url stdin {n}     "{url.rstrip()}"')
            main(url, args)

    for url in args.url:
        n += 1
        url = url.rstrip()
        log.debug(f'url arg {n}       "{url.rstrip()}"')
        main(url, args)
