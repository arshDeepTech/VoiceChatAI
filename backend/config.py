import torch

# System Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
UPLOAD_FOLDER = "uploads"
CLEANUP_INTERVAL = 300  # 5 minutes in seconds

# Audio Configuration
SAMPLE_RATE = 24000 