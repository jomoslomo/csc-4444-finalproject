#!/bin/bash

# Start the Node.js server
echo "Starting Node.js server..."
cd ws-server-example-nodejs
npm start &
cd ..

# Navigate to the CV directory, install Python requirements, and run the Python script
echo "Preparing Python environment..."
cd CV
# Uncomment the next line if you need to activate a virtual environment
# source venv/bin/activate
echo "Installing Python requirements..."
pip install -r requirements.txt
echo "Starting the Python script hit.py..."
python3 hit.py &
cd ..

# Start the HTTP server for the xArmEX project
echo "Starting xArmEX project..."
http-server ./xArmEX -p 8000 &

# Keep script running until all child processes are killed
wait
