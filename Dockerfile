
FROM python:3.10


# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./app.py /app
COPY ./requirements.txt /app
COPY ./templates /app/templates

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["gunicorn", "-b 0.0.0.0:5000", "app:app"]
