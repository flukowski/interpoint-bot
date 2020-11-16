#! /bin/sh

git pull origin master && (killall python3 || true) && source ~/.bash_profile && (nohup python3 -u ralf.py > out.log 2>&1 &)
