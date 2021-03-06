# web_app/routes/stats_routes.py

from flask import Blueprint, request, jsonify, render_template

from sklearn.linear_model import LogisticRegressionCV # for example
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import DecisionTreeClassifier 
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import category_encoders as ce  
from web_app.models import User, Tweet
from web_app.services.basilica_service import connection as basilica_api_client

stats_routes = Blueprint("stats_routes", __name__)

@stats_routes.route("/predict", methods=["POST"])
def predict():
    print("PREDICT ROUTE...")
    print("FORM DATA:", dict(request.form))
    #> {'screen_name_a': 'elonmusk', 'screen_name_b': 's2t2', 'tweet_text': 'Example tweet text here'}
    screen_name_a = request.form["screen_name_a"]
    screen_name_b = request.form["screen_name_b"]
    tweet_text = request.form["tweet_text"]

    print("-----------------")
    print("FETCHING TWEETS FROM THE DATABASE...")
    # todo: wrap in a try block in case the user's don't exist in the database
    user_a = User.query.filter_by(screen_name=screen_name_a).one()
    user_b = User.query.filter_by(screen_name=screen_name_b).one()
    user_a_tweets = user_a.tweets
    user_b_tweets = user_b.tweets
    #user_a_embeddings = [tweet.embedding for tweet in user_a_tweets]
    #user_b_embeddings = [tweet.embedding for tweet in user_b_tweets]
    print("USER A", user_a.screen_name, len(user_a.tweets))
    print("USER B", user_b.screen_name, len(user_b.tweets))




    print("-----------------")
    print("TRAINING THE MODEL...")
    embeddings = []
    labels = []
    for tweet in user_a_tweets:
        labels.append(user_a.screen_name)
        embeddings.append(tweet.embedding)
        

    for tweet in user_b_tweets:
        labels.append(user_b.screen_name)
        embeddings.append(tweet.embedding)
        
    pipeline = make_pipeline(ce.OrdinalEncoder(), 
    DecisionTreeClassifier(min_samples_leaf=3, random_state=42, max_depth=9))

    pipeline.fit(embeddings, labels)
    
    print("classifier training score:", pipeline.score(embeddings, labels))
    print("-----------------")
    print("MAKING A PREDICTION...")
    
    #result_a = classifier.predict([user_a_tweets[0].embedding])
    #result_b = classifier.predict([user_b_tweets[0].embedding])

    
    example_embedding = basilica_api_client.embed_sentence(tweet_text, model="twitter")
    result = pipeline.predict([example_embedding])
    
    #breakpoint()

    #return jsonify({"message": "RESULTS", "most_likely": result[0]})
    return render_template("prediction_results.html",
        screen_name_a=screen_name_a,
        screen_name_b=screen_name_b,
        tweet_text=tweet_text,
        screen_name_most_likely= result[0]
    )