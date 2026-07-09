#!/bin/bash
set -e

echo "[*] Starting bgutil PO token provider server..."
node /opt/bgutil-provider/server/build/main.js &
BGUTIL_PID=$!

# Give bgutil server a moment to boot up before API starts hitting it
sleep 2

echo "[*] Starting YUKI YT API (uvicorn)..."
uvicorn YUKIYTAPI.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# If either process dies, kill the other and exit (so Railway restarts container)
wait -n $BGUTIL_PID $API_PID
exit $?

