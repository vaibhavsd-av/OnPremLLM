# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install required system dependencies (including curl and poppler-utils)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    poppler-utils  # This installs the Poppler utilities, including pdfinfo

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the required Python packages
RUN pip install -r requirements.txt

# Install Streamlit for running the frontend UI
RUN pip install streamlit

# Copy the rest of the project into the container
COPY . .

# Expose port 8501 for Streamlit (default port)
EXPOSE 8501

# Run the bash script to start the app
CMD ["bash", "start.sh"]
