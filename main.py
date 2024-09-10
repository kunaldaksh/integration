import telebot
from pymongo import MongoClient
import uuid
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi
import telebot
import pymongo
import random
import string
import telebot
from pymongo import MongoClient
import string
import random
from flask import Flask, render_template, redirect
import os

# Initialize the bot with your bot token
bot = telebot.TeleBot("7465020548:AAGUuwKtGE6mRTN0HIHIY9gx8SD-ldGGER0")
MONGO_URI = os.environ.get('MONGO_URI')

# MongoDB connection setup
client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client["modiurl_db"]
collection = db["links"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Flask app
app = Flask(__name__)

# Generate a unique ID for each link
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Telegram bot handler for receiving links
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Send me the link you want to shorten:")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    original_link = message.text
    unique_id = generate_unique_id()

    # Save to MongoDB
    collection.insert_one({
        "unique_id": unique_id,
        "original_link": original_link
    })

    # Generate the custom URL
    custom_url = f"https://kunaldaksh.github.io/modiurl/{unique_id}"

    # Respond to the user
    bot.reply_to(message, f"Your link has been shortened: {custom_url}")

# Route for the shortened link
@app.route('/<unique_id>')
def redirect_to_link(unique_id):
    # Retrieve the original link from MongoDB
    link_data = collection.find_one({"unique_id": unique_id})

    if link_data:
        return render_template('index.html', original_link=link_data['original_link'])
    else:
        return "Invalid URL", 404

# HTML file served at the custom URL
@app.route('/index.html')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ModiJiUrl.com</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
        <style>
            /* Add your existing CSS styles here */
        </style>
    </head>
    <body>
        <div class="header">ModiJiUrl.com</div>
        <div class="container">
            <div class="message">Your link is almost ready.</div>
            <div class="timer" id="timer">10 Seconds</div>
            <button class="wait-btn" id="wait-btn" disabled>PLEASE WAIT...</button>
            <div class="ready-link" id="ready-link">
                <p>Your link is ready: <a href="{{ original_link }}" target="_blank">Click here</a></p>
            </div>
        </div>
        <footer>© 2024 ModiJiUrl. All rights reserved.</footer>
        <script>
            let timeLeft = 10;
            const timerElement = document.getElementById('timer');
            const waitBtn = document.getElementById('wait-btn');
            const readyLink = document.getElementById('ready-link');

            const countdown = setInterval(() => {
                if (timeLeft <= 0) {
                    clearInterval(countdown);
                    timerElement.textContent = "0 Seconds";
                    waitBtn.textContent = "Link Ready!";
                    waitBtn.style.opacity = "1";
                    waitBtn.style.cursor = "pointer";
                    waitBtn.disabled = false;
                    readyLink.style.display = "block";
                } else {
                    timerElement.textContent = `${timeLeft} Seconds`;
                }
                timeLeft -= 1;
            }, 1000);
        </script>
    </body>
    </html>
    '''

# Run Flask app
if __name__ == '__main__':
    bot.polling()
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
