#!/bin/bash

if [ -f ./.env ]; then
    rm ./.env
fi
NOW=$(TZ=IST-5:30 date +'%d/%m/%Y %H:%M:%S')
env_content="NOW="$NOW"\n"
env_content=$env_content"ENV=DEV""\n"

printf "$env_content" > ./.env
docker-compose -f docker-compose.yml up --remove-orphans --build -d