# In gunicorn.conf.py

# Network settings
bind = "0.0.0.0:8000"

# Number of worker processes
workers = 2  # A good starting point

# --- The Important Part: Timeout ---
# Increase the timeout to allow the heavy models to load
timeout = 120

# --- The Professional Optimization: Preload App ---
# This loads the app once in the main process, saving a huge amount of memory.
# All worker processes will share this single instance.
preload_app = True