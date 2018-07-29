#!/bin/sh

ps auxw | grep pserve | grep -v grep > /dev/null

if [ $? != 0 ]
then
  sudo /home/ubuntu/src/singleton/env/bin/pserve /home/ubuntu/src/singleton/production.ini --reload & #> /dev/null
else
  echo "Pyramid server already running"
fi
