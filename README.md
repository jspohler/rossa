# AI-AI-Captn 

![rossa](https://github.com/SMohabey/AI-AI-Caption/blob/main/rossa.png)

A personalised internal chatbot for Rossmann as the result of the Ai-Ai-Captn Hackathon of the Digital Industry Hub Bremen. I contributed in form of prompt engineering, testing and transforming the provided excel sheet into a database.


# Chatbot Setup Guide

This guide will help you set up and run the chatbot locally.

## Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-folder>
```

## Step 2: Install Dependencies

Navigate to the `chatbot` folder and install the required Python libraries using the `requirements.txt` file:

```bash
cd chatbot
pip install -r requirements.txt
```

## Step 3: Create Environment Files

Next, you need to create two `.env` files, one in the `/chatbot` folder and one in the `/data` folder.

### .env file in `/chatbot` folder

Create a file named `.env` inside the `chatbot` folder and add the following content:

```
# OpenAI API Key
OPENAI_API_KEY="your-openai-api-key"

# Database Configuration
DATABASE_HOST="localhost"
DATABASE_PORT="3306"
DATABASE_USER="root"
DATABASE_PASSWORD="root"
DATABASE_NAME="userinformation"
```

Replace `"your-openai-api-key"` with your actual OpenAI API key.

### .env file in `/data` folder

Similarly, create a file named `.env` inside the `data` folder and add the following content:

```
# Database Configuration
DATABASE_HOST="localhost"
DATABASE_PORT="3306"
DATABASE_USER="root"
DATABASE_PASSWORD="root"
DATABASE_NAME="userinformation"
```

## Step 4: Initialize the Database

Navigate to the `/data` folder and run the `data_init.py` script to initialize the database using the data in `data.xlsx`:

```bash
cd ../data
python data_init.py
```

This will set up the database with the necessary tables and data.

## Step 5: Run the Chatbot Application

Finally, to start the chatbot application, run the following command from the root of your project:

```bash
streamlit run /chatbot/main.py
```

This will launch the chatbot in your browser, and you can begin interacting with it.

---

### Additional Notes:
- Make sure that your database server (MySQL or equivalent) is up and running before initializing the database or launching the chatbot.
- Ensure all necessary ports are correctly configured and not blocked by firewalls.

This completes the setup guide for the chatbot project. Enjoy building and customizing the chatbot!


