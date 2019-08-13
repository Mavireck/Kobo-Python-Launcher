#! /bin/sh

# [ -e info.log ] && [ "$(stat -c '%s' info.log)" -gt $((1<<18)) ] && mv info.log archive.log

# RUST_BACKTRACE=1 ./plato >> info.log 2>&1 || mv info.log crash.log

# ./nickel.sh &


./plato

./nickel.sh &

