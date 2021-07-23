#!/bin/sh

entity_name="$1"
stage="$2"

if [ -d "/etc/yip.d/$entity_name/" ]; then
    yip -s "$stage" "/etc/yip.d/$entity_name/"
fi