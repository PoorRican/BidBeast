FROM python:3.12-alpine
LABEL authors="PoorRican"

##################
# SETUP BACKEND  #
##################

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "main.py"]
