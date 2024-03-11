
import csv
from flask import Flask, jsonify, request
from werkzeug.exceptions import Unauthorized
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    

app = Flask(__name__)


# Fonction pour charger les données depuis le fichier CSV
def load_credentials():
    credentials = []
    with open('credentials.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            credentials.append(row)
    return credentials

@app.route('/')
def index():
    return 'Hello, Flask!'

@app.route('/status')
def api_status():
    # Nous pouvons ajouter ici des vérifications supplémentaires pour déterminer l'état de l'API
    status_code = 1

    # Renvoie le statut sous forme de réponse JSON
    return jsonify({"status": status_code})

# Route pour le message de salutation
@app.route('/welcome')
def welcome_user():
    # Charger les données depuis le fichier CSV
    credentials = load_credentials()

    # Obtenir le nom d'utilisateur à partir de la chaîne de requête
    username = request.args.get('username', '')

    # Rechercher le nom d'utilisateur dans les données chargées
    user_data = next((user for user in credentials if user['username'] == username), None)

    if user_data:
        # Renvoyer un message de salutation avec le nom d'utilisateur
        welcome_message = f"Bonjour, {username}! Bienvenue sur sentixAna API!"
        return jsonify({"message": welcome_message})
    else:
        # Renvoyer un message d'erreur si le nom d'utilisateur n'est pas trouvé
        return jsonify({"error": "Utilisateur non trouvé"}), 404

# Route pour obtenir les permissions
@app.route('/permissions', methods=['POST'])
def get_permissions():
    # Charger les données depuis le fichier CSV
    credentials = load_credentials()

    # Récupérer les informations d'authentification depuis le corps de la requête JSON
    auth_data = request.get_json()
    username = auth_data.get('username', '')
    password = auth_data.get('password', '')

    # Rechercher l'utilisateur dans les données chargées
    user_data = next((user for user in credentials if user['username'] == username and user['password'] == password), None)

    if user_data:
        # Renvoyer la liste des permissions
        permissions = {'v1': user_data['v1'], 'v2': user_data['v2']}
        
        # Ajouter un en-tête à la réponse
        response = jsonify(permissions)
        response.headers['Username'] = username
        response.headers['V1-Value'] = user_data['v1']
        response.headers['V2-Value'] = user_data['v2']
        
        return response
    else:
        # Renvoyer une erreur si l'utilisateur n'est pas trouvé
        raise Unauthorized("User is not allowed")


# Route pour obtenir le score de sentiment avec le modèle v1
@app.route('/v1/sentiment', methods=['POST'])
#@login_required
def get_v1_sentiment_score():
    # Récupérer les informations d'identification depuis l'en-tête
    auth_header = request.headers.get('Authorization')
    if auth_header:
        username, password = auth_header.split('=')
        user_data = next((user for user in load_credentials() if user['username'] == username and user['password'] == password), None)
        
        if user_data:
            # Récupérer la phrase depuis le corps de la requête JSON
            sentence = request.get_json().get('sentence', '')
            # Vérifier la permission v1
            if user_data['v1'] == '1':
                
                # Calculer un score de sentiment aléatoire entre -1 et 1 avec 2 décimales si v1=1
                sentiment_score = round(random.uniform(-1, 1), 2)
                
                # Renvoyer le score de sentiment
                return jsonify({"sentence_text": sentence, "sentiment_score": sentiment_score})

            else:
                    return jsonify({"error": "Insufficient permission for v1"}), 403  # 403 Forbidden

    # Renvoyer une erreur si l'utilisateur n'est pas authentifié
    return jsonify({"error": "Unauthorized"}), 401

# Route pour obtenir le score de sentiment avec le modèle v1
@app.route('/v2/sentiment', methods=['POST'])
#@login_required
def get_v2_sentiment_score():
    # Récupérer les informations d'identification depuis l'en-tête
    auth_header = request.headers.get('Authorization')
    if auth_header:
        username, password = auth_header.split('=')
        user_data = next((user for user in load_credentials() if user['username'] == username and user['password'] == password), None)
        
        if user_data:
            # Récupérer la phrase depuis le corps de la requête JSON
            sentence = request.get_json().get('sentence', '')

            if user_data['v2'] == '1':

                # Placeholder : calculer un score de sentiment aléatoire entre -1 et 1
                analyzer = SentimentIntensityAnalyzer()
                vs = analyzer.polarity_scores(sentence)
                print("{:-<65} {}".format(sentence, str(vs)))
                
                # Renvoyer le score de sentiment
                return jsonify({"sentence_text": sentence, "sentiment_score": str(vs)})
            
            else:
                return jsonify({"error": "Insufficient permission for v2"}), 403  # 403 Forbidden
    
    # Renvoyer une erreur si l'utilisateur n'est pas authentifié
    return jsonify({"error": "Unauthorized"}), 401

