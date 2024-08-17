# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12.0

# Set the working directory in the container
WORKDIR /src

# Copy the requirements file from the current directory to the container
COPY requirements.txt .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get -y install gcc make \
    && rm -rf /var/lib/apt/lists/*s
# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install xvfb -y
RUN apt-get install -y google-chrome-stable
RUN python3 --version
RUN pip3 --version
RUN pip install --no-cache-dir --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

# Copy the rest of your application source code from the src directory
COPY ./src .

CMD ["python", "main.py"]
