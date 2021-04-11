#!/bin/bash

entity_name="$1"

if [ -d "/etc/entities/$entity_name/group/" ]; then
    for filename in /etc/entities/$entity_name/group/*.yaml; do
        entities apply -f /etc/group $filename
    done
fi

if [ -d "/etc/entities/$entity_name/passwd/" ]; then
    for filename in /etc/entities/$entity_name/passwd/*.yaml; do
        entities apply -f /etc/passwd $filename
    done
fi