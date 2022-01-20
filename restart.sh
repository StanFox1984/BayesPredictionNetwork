#!/bin/bash

if [ -f pid_file ]
then
pid=`cat pid_file`
kill $pid
echo "killed $pid"
fi

python server.py 2>&1

pid="$!"

echo $pid > pid_file