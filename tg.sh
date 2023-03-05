#!/bin/bash

help="
$(basename "$0") -- Telegram sendMessage via curl

https://core.telegram.org/bots/api#sendmessage

EXAMPLES:
    $(basename "$0") --chat_id @big_papi_channel --message 'si papi'
    $(basename "$0") --message \$(echo '{\"link\":\"www.google.com\"}' | jq '.link')
    $(basename "$0") --message \$(./booble 'https://bbs.io-tech.fi/forums/myydaeaen.80/?order=post_date&direction=desc' | jq '.link')

    booble.py --format '{link}' 'https://bbs.io-tech.fi/forums/myydaeaen.80/?order=post_date&direction=desc' | $(basename "$0")

OPTIONS:
    -h, --help
    -v, --verbose
    --token x
    --chat_id @big_papi_channel
    --message \"si papi\"
    --disable_notification
    --disable_web_page_preview

SETUP
    1. Create telegram bot (example name big_papi)
      https://t.me/botfather
        /start
        /newbot
        big_papi
        big_papi_bot

    2. Create public channel (big_papi_channel)

    3. Add members > search big_papi_bot

    4. Add token and chat_id to private.sh, or pass as arguments

    5. ./tg --chat_id @big_papi_channel --message 'si papi'"

# Parse args
token="1172593241:AAE1mBUALAMPCQx2RE-Rp0PoLFojJd3KVbA"
chat_id="-1001454128731"
disable_notification="false"
disable_web_page_preview="false"
timeout="30"

script_dir="$(dirname "$0")"
[ -f "$script_dir/private.sh" ] && . "$script_dir/private.sh"

while [ $# -gt 0 ]; do

  if [[ $1 == *"-h"* ]] || [[ $1 == *"--help"* ]]; then
    echo "$help"
    exit 1

  elif [[ $1 == *"-v"* ]]; then
    declare verbose="true"

  elif [[ $1 == *"--disable_notification"* ]] || [[ $1 == *"--disable_web_page_preview"* ]]; then
    param="${1/--/}"
    declare $param="true"

  elif [[ $1 == *"--"* ]]; then
    param="${1/--/}"
    declare $param="$2"
  fi

  shift
done

if [ "$verbose" ]; then
  echo 'args'
  echo "    token                    : \"$token\""
  echo "    chat_id                  : \"$chat_id\""
  echo "    disable_notification     : \"$disable_notification\""
  echo "    disable_web_page_preview : \"$disable_web_page_preview\""
fi

# Telegram sendMessage
#
# https://core.telegram.org/bots/api#sendmessage
#
# $1: chat_id => "@channel_id"
# $2: text    => "Hello"
send () {
  message=$(sed -e 's/^"//' -e 's/"$//' <<< "$2")

  response=$(curl "https://api.telegram.org/bot$token/sendMessage" \
    -X POST                                                        \
    -H "Content-Type: application/json"                            \
    --silent                                                       \
    -d "{
          \"chat_id\": \"$1\",
          \"text\": \"$message\",
          \"disable_notification\": $disable_notification,
          \"disable_web_page_preview\": $disable_web_page_preview
        }") &

  if [ "$verbose" ]; then
    echo "message : $message"
    echo "response : $response"
  fi
}

# do it
#
# stdin if --message not set
if [ -z "$message" ]; then
  while read -t "$timeout" line; do
    if [ "$verbose" ]; then echo "stdin"; fi
    send "$chat_id" "$line"

    # notify once only
    disable_notification="true"
  done < /dev/stdin
else
  if [ "$verbose" ]; then echo "message arg"; fi
  send "$chat_id" "$message"
fi


