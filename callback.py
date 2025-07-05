from flask import Flask, request, redirect
import requests
import os


CLIENT_ID = 1300736542490230804
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
app = Flask(__name__)
REDIRECT_URI = 'https://discord-4rrr.onrender.com/'

@app.route('/')
def index():
    return f'<a href="https://discord.com/oauth2/authorize?client_id=1300736542490230804&redirect_uri=https://discord-4rrr.onrender.com/&response_type=code&scope=bot+applications.commands&permissions=8">Login with Discord</a>'

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_json = token_response.json()
    access_token = token_json['access_token']

    # Gebruik access_token om user info op te halen
    user_response = requests.get(
        'https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_json = user_response.json()

    return f"Hello {user_json['username']}#{user_json['discriminator']}!"

if __name__ == '__main__':
    app.run(debug=True)