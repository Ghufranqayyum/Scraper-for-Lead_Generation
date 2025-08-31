# Use official Python image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y wget gnupg unzip curl \
    fonts-liberation libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxi6 libxtst6 libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libdrm2 libgbm1 libasound2 libxrandr2 libxss1 libxkbcommon0 \
    libpangocairo-1.0-0 libpango-1.0-0 libcups2 libatk1.0-0

# Add Google Chrome repo + key (new method, since apt-key is deprecated)
RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (for Selenium)
# Install ChromeDriver (for Selenium)
RUN wget -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/119.0.6045.105/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

# Set ChromeDriver path environment variable
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set display port (needed for Chrome in headless mode)
ENV DISPLAY=:99

# Set work directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start Flask app
# Fixed (shell form that expands $PORT):# Change your current CMD line to:
CMD ["python", "app.py"]




