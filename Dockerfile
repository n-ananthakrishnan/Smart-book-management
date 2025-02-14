# Use an official lightweight Python image
FROM python:3.10

# Install system dependencies (important for zbar and OpenCV)
RUN apt-get update && apt-get install -y libgl1-mesa-glx libzbar0

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 (Flask default)
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
