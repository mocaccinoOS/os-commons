#!/bin/sh

entity_name="$1"
yipfile="$2"

if [ ! -d "/etc/yip.d/$entity_name/" ]; then
    mkdir /etc/yip.d/$entity_name/
fi

cp -rf $yipfile /etc/yip.d/$entity_name/