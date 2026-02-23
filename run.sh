set -euo pipefail

# create env
if [ ! -d "venv" ]; then
  echo "Creating virtual environment…"
  python3 -m venv venv
fi

# activate venv
if [ -f "venv/bin/activate" ]; then
  # Unix-подобные системы
  # shellcheck source=/dev/null
  source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
  # Windows Git-Bash / MSYS
  # shellcheck source=/dev/null
  source venv/Scripts/activate
else
  echo "ERROR: Cannot find venv activation script" >&2
  exit 1
fi

# pip and dependencies
echo "Installing dependencies…"
pip install --upgrade pip
pip install fastapi uvicorn

# uvicorn
LOG_FILE="uvicorn.log"
echo "Starting server… logs -> $LOG_FILE"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo "✅ Server is running with PID $PID"
echo "   To stop it, run: kill $PID"