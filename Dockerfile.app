FROM python:3.10-slim

# Create a non-root user and set ownership of the /app directory
RUN useradd -m flask

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /usr/src/app
COPY flask-monitor.py requirements.txt /app/

# Install all packages & Create directory for logs &Change ownership of the /app directory to the new user
RUN pip3 install --no-cache-dir -r /app/requirements.txt && mkdir /app/logs && chown -R flask:flask /app

# Switch to the non-root user
USER flask

# Expose the two ports
EXPOSE 8080
EXPOSE 5000
# Run the Python file when the container launches
#Use ENTRYPOINT to define the executable
ENTRYPOINT ["python3", "flask-monitor.py","-i"]

#Use CMD to provide default arguments
CMD ["5"]