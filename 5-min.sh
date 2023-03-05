#!/bin/bash

hour=$(date +%H)
(( $hour < 8 && $hour > 0 )) && exit 0

cd "$(dirname "$0")"

sahkopoyta='https://www.tori.fi/uusimaa?q=s%E4hk%F6p%F6yt%E4&cg=3020&w=1&st=s&st=g&c=0&ca=18&l=0&f=p&md=th'
kyykkyteline='https://www.tori.fi/uusimaa?q=kyykky*&cg=4010&w=1&st=s&st=g&c=4024&ps=&pe=&ca=18&l=0&md=th'
tanko='https://www.tori.fi/uusimaa/urheilu_ja_ulkoilu/kuntoilu_ja_fitness?ca=18&q=tanko&st=s&st=g&w=1&cg=4010&c=4024'
xps='https://www.tori.fi/koko_suomi?q=dell+xps&cg=5030&w=3&st=s&c=0&ps=4&pe=&ca=18&l=0&f=p&md=th'
nuc='https://www.tori.fi/koko_suomi?q=nuc+OR+%22mini+pc%22&cg=5030&w=3&st=s&st=g&c=5034&ps=&pe=&ca=18&l=0&f=p&md=th'
dyson='https://www.tori.fi/koko_suomi?q=dyson+AND+V10+OR+dyson+AND+V11&cg=0&w=1&st=s&st=g&ca=18&l=0&md=th'
sony='https://www.tori.fi/koko_suomi?q=wf-1000*+OR+wh-1000*+OR+quietcomfort+OR+noise+cancelling+OR+vastamelu*&cg=0&w=3&st=s&ca=18&l=0&md=th'

log="log/5-min.log"

./booble.py "$sony"         --format {link} | tee -a $log | ./tg.sh
./booble.py "$kyykkyteline" --format {link} | tee -a $log | ./tg.sh
