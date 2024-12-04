#!/bin/bash

ENV_NAME="voicechatai_env"
REQUIREMENTS_FILE="requirements.txt"

echo "Creating conda environment: $ENV_NAME"
conda create --name $ENV_NAME python=3.10 -y

# Activate the environment
echo "Activating the environment: $ENV_NAME"
source activate $ENV_NAME

echo "Installing dependencies from $REQUIREMENTS_FILE"
pip install -r $REQUIREMENTS_FILE

echo "Environment setup completed successfully!"
