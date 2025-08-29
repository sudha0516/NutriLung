from flask import Flask, render_template, request,session
import mysql.connector
import pandas as pd

import joblib


app = Flask(__name__)
app.secret_key = 'admin'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='lung_db'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']
        if password == c_password:
            query = "SELECT UPPER(email) FROM users"
            email_data = retrivequery2(query)
            email_data_list = []
            for i in email_data:
                email_data_list.append(i[0])
            if email.upper() not in email_data_list:
                query = "INSERT INTO users (email, password) VALUES (%s, %s)"
                values = (email, password)
                executionquery(query, values)
                return render_template('login.html', message="Successfully Registered!")
            return render_template('register.html', message="This email ID is already exists!")
        return render_template('register.html', message="Conform password is not match!")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT UPPER(email) FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email.upper() in email_data_list:
            query = "SELECT UPPER(password) FROM users WHERE email = %s"
            values = (email,)
            password__data = retrivequery1(query, values)
            if password.upper() == password__data[0][0]:
                global user_email
                user_email = email
                name = password__data[0][0]
                session['name'] = name
                return render_template('home.html',message= f"Welcome to Home page {name}")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/upload',methods = ["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        df = pd.read_csv(file)
        df = df.to_html()
        return render_template('upload.html', df = df)
    return render_template('upload.html')


@app.route('/model',methods =["GET","POST"])
def model():
    if request.method == "POST":
        algorithams = request.form["algo"]
        if algorithams == "1":
            accuracy = 98.17
            msg = 'Accuracy  for  Random Forest is ' + str(accuracy) + str('%')
        elif algorithams == "2":
            accuracy = 100
            msg = 'Accuracy  for XGBoost  is ' + str(accuracy) + str('%')
        elif algorithams == "3":
            accuracy = 100
            msg = 'Accuracy  for Voting Classifier is ' + str(accuracy) + str('%')
        elif algorithams == "4":
            accuracy = 99
            msg = 'Accuracy  for SVM is ' + str(accuracy) + str('%')

        elif algorithams == "5":
            accuracy = 98.63
            msg = 'Accuracy  for SVM is ' + str(accuracy) + str('%')
        
        return render_template('model.html',msg=msg,accuracy = accuracy)
    return render_template('model.html')


import random 

@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    result = None
    recommendations = None
    
    if request.method == "POST":
        air_pollution = int(request.form['Air Pollution'])
        alcohol_use = int(request.form['Alcohol use'])
        genetic_risk = int(request.form['Genetic Risk'])
        balanced_diet = int(request.form['Balanced Diet'])
        obesity = int(request.form['Obesity'])
        smoking = int(request.form['Smoking'])
        passive_smoker = int(request.form['Passive Smoker'])
        chest_pain = int(request.form['Chest Pain'])
        coughing_of_blood = int(request.form['Coughing of Blood'])
        fatigue = int(request.form['Fatigue'])

        model = joblib.load('svm_model.joblib')

        def prediction_function(inputs):
            classes = {0: "High", 1: "Medium", 2: "Low"}
            prediction = model.predict(inputs)
            return classes[prediction[0]]

        inputs = [[air_pollution, alcohol_use, genetic_risk, balanced_diet, obesity, smoking, passive_smoker, chest_pain, coughing_of_blood, fatigue]]
        result = prediction_function(inputs)
        
        # Define detailed recommendations for each risk level
        high_risk_recommendations = [
            "Given your high risk, it's crucial to consult a pulmonologist or oncologist immediately for a comprehensive lung health evaluation and potential early screening.",
            "To reduce your high risk, you should completely stop smoking and avoid secondhand smoke exposure in all environments, including at home and work.",
            "Limiting alcohol consumption to no more than one drink per day can significantly help lower your risk of developing serious respiratory conditions.",
            "Incorporating at least 30 minutes of moderate exercise five times a week can help improve lung capacity and overall cardiovascular health.",
            "Eating a diet rich in antioxidants from colorful fruits and vegetables may help protect your lungs from further damage and inflammation.",
            "Monitoring symptoms like persistent cough, chest pain, or fatigue and reporting any changes to your doctor promptly is extremely important."
        ]
        
        medium_risk_recommendations = [
            "Schedule a consultation with your primary care physician to discuss personalized strategies for reducing your moderate lung cancer risk factors.",
            "Gradually reducing your smoking habit with a goal to quit completely within the next three months would significantly benefit your lung health.",
            "Consider replacing alcoholic beverages with healthier alternatives like herbal teas or infused waters to decrease your moderate risk level.",
            "Aim for a balanced diet containing at least five servings of varied vegetables daily to boost your body's natural defense systems.",
            "Engaging in regular physical activity, such as brisk walking for 30 minutes daily, can help manage weight and improve respiratory function.",
            "Be mindful of air quality alerts and limit outdoor activities when pollution levels are high to protect your respiratory system."
        ]
        
        low_risk_recommendations = [
            "While your risk is low, maintaining annual check-ups with your healthcare provider ensures early detection of any potential health changes.",
            "Continue your healthy habits of not smoking and limit exposure to environments where others might be smoking around you.",
            "Moderate alcohol consumption to social occasions only, keeping within recommended limits of one drink per day for optimal health.",
            "Sustain your balanced diet by including a variety of whole grains, lean proteins, and colorful fruits and vegetables at each meal.",
            "Regular aerobic exercise like swimming, cycling, or jogging three to four times weekly helps maintain strong lung capacity and function.",
            "Stay informed about new research in lung health prevention to maintain your current low-risk status as you age."
        ]
        
        # Select 3 random recommendations from the appropriate list
        if result == "High":
            recommendations = random.sample(high_risk_recommendations, 3)
        elif result == "Medium":
            recommendations = random.sample(medium_risk_recommendations, 3)
        elif result == "Low":
            recommendations = random.sample(low_risk_recommendations, 3)

    return render_template('prediction.html', prediction=result, recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug = True)