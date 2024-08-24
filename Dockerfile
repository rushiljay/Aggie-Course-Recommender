# Use an official Python runtime as a parent image
FROM python:3.12.0

# Set the working directory in the container
WORKDIR /src

# Copy the requirements file from the current directory to the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80

# Copy the rest of your application source code from the src directory
COPY ./src .

CMD ["python", "main.py"]
