#!/bin/bash

if [ -f pid_file ]
then
pid=`cat pid_file`
kill $pid
echo "kill $pid"
fi

python server.py &

pid="$!"

echo $pid > pid_file