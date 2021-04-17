#!/bin/sh

entity_name="$1"

if [ -d "/etc/entities/$entity_name/group/" ]; then
    if [ ! -e /etc/group ]; then
        touch /etc/group
    fi
    for filename in $(ls /etc/entities/$entity_name/group); do
        entities apply -f /etc/group /etc/entities/$entity_name/group/$filename
    done
fi

if [ -d "/etc/entities/$entity_name/passwd/" ]; then
    if [ ! -e /etc/passwd ]; then
        touch /etc/passwd
    fi
    for filename in $(ls /etc/entities/$entity_name/passwd); do
        entities apply -f /etc/passwd /etc/entities/$entity_name/passwd/$filename
    done
fi
