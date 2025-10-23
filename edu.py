from flask import Flask, render_template_string, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "env_platform_secret"

# ----------------------------
# Data
# ----------------------------
students = {}  # name -> {"score": int, "badges": []}
leaderboard = []

quiz_questions = [
    {"question": "Which gas is a major contributor to global warming?", "options": ["Oxygen", "CO2", "Nitrogen", "Helium"], "answer": "CO2"},
    {"question": "Which of these is recyclable?", "options": ["Plastic bottle", "Sand", "Glass bottle", "All"], "answer": "All"},
    {"question": "What is the main cause of deforestation?", "options": ["Urbanization", "Agriculture", "Logging", "All"], "answer": "All"},
]

eco_challenges = [
    "Use a reusable water bottle today.",
    "Turn off unused lights for the whole day.",
    "Plant one tree this week.",
    "Recycle your old paper and plastic."
]

ai_responses = {
    "climate change": "Climate change refers to long-term shifts in temperatures and weather patterns.",
    "recycling": "Recycling helps reduce waste and conserve resources.",
    "carbon footprint": "Your carbon footprint is the total CO2 emissions caused by your activities.",
    "pollution": "Pollution is the introduction of harmful substances into the environment."
}

# ----------------------------
# Common CSS
# ----------------------------
style = """
<style>
body { font-family: Arial, sans-serif; background: #e0f7fa; color: #00695c; margin: 0; padding: 0; }
h1, h2 { text-align: center; }
.container { width: 90%; max-width: 800px; margin: 20px auto; padding: 20px; background: #ffffff; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
a { text-decoration: none; color: #004d40; font-weight: bold; }
a:hover { color: #00796b; }
button, input[type=submit] { background: #00796b; color: #ffffff; border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; margin-top: 10px; }
button:hover, input[type=submit]:hover { background: #004d40; }
ul { list-style: none; padding-left: 0; }
ul li { margin: 5px 0; }
.badge { display: inline-block; background: #ffd600; color: #004d40; padding: 5px 10px; border-radius: 15px; margin: 5px; font-weight: bold; }
input[type=text], input[type=number] { padding: 8px; border-radius: 8px; border: 1px solid #ccc; width: 80%; }
</style>
"""

# ----------------------------
# Templates
# ----------------------------
index_html = """
<!DOCTYPE html>
<html>
<head><title>Gamified Environmental Platform</title>""" + style + """</head>
<body>
<div class="container">
<h1>🌱 Welcome to Gamified Environmental Education Platform</h1>
<form method="post" action="/set_name">
    <input type="text" name="name" placeholder="Enter your name" required>
    <input type="submit" value="Start">
</form>
</div>
</body>
</html>
"""

menu_html = """
<!DOCTYPE html>
<html>
<head><title>Main Menu</title>""" + style + """</head>
<body>
<div class="container">
<h1>Hello {{name}}! Choose an option:</h1>
<ul>
    <li><a href="/quiz">📚 Take Quiz</a></li>
    <li><a href="/challenge">🌱 Eco Challenge</a></li>
    <li><a href="/carbon">⚡ Carbon Footprint Calculator</a></li>
    <li><a href="/chat">🤖 AI Chatbot</a></li>
    <li><a href="/leaderboard">🏆 Leaderboard</a></li>
</ul>
<h2>Your Badges 🏅</h2>
{% if badges %}
<div>
{% for b in badges %}
    <span class="badge">🌿 {{b}}</span>
{% endfor %}
</div>
{% else %}
<p>No badges yet. Complete eco-challenges to earn badges!</p>
{% endif %}
</div>
</body>
</html>
"""

quiz_html = """
<!DOCTYPE html>
<html>
<head><title>Quiz</title>""" + style + """</head>
<body>
<div class="container">
<h1>📚 Quiz for {{name}}</h1>
<form method="post">
{% for i in range(questions|length) %}
    <p><b>{{questions[i].question}}</b></p>
    {% for opt in questions[i].options %}
        <input type="radio" name="q{{i}}" value="{{opt}}" required> {{opt}}<br>
    {% endfor %}
{% endfor %}
<input type="submit" value="Submit Quiz">
</form>
<a href="/menu">⬅ Back to Menu</a>
</div>
</body>
</html>
"""

challenge_html = """
<!DOCTYPE html>
<html>
<head><title>Eco Challenge</title>""" + style + """</head>
<body>
<div class="container">
<h1>🌱 Eco Challenge</h1>
<p>{{challenge}}</p>
<form method="post">
    <input type="hidden" name="challenge" value="{{challenge}}">
    <input type="submit" value="Complete Challenge & Get Badge">
</form>
<a href="/menu">⬅ Back to Menu</a>
</div>
</body>
</html>
"""

carbon_html = """
<!DOCTYPE html>
<html>
<head><title>Carbon Footprint</title>""" + style + """</head>
<body>
<div class="container">
<h1>⚡ Carbon Footprint Calculator</h1>
<form method="post">
    Electricity used per month (kWh): <input type="number" name="electricity" step="0.1" required><br>
    Travel by car per month (km): <input type="number" name="travel" step="0.1" required><br>
    <input type="submit" value="Calculate">
</form>
{% if result is not none %}
<p><b>Estimated CO2 footprint:</b> {{result}} kg CO2/month</p>
{% endif %}
<a href="/menu">⬅ Back to Menu</a>
</div>
</body>
</html>
"""

chat_html = """
<!DOCTYPE html>
<html>
<head><title>AI Chatbot</title>""" + style + """</head>
<body>
<div class="container">
<h1>🤖 AI Chatbot</h1>
<form method="post">
    Ask me anything about environment: <input type="text" name="question" required>
    <input type="submit" value="Ask">
</form>
{% if response %}
<p><b>Response:</b> {{response}}</p>
{% endif %}
<a href="/menu">⬅ Back to Menu</a>
</div>
</body>
</html>
"""

leaderboard_html = """
<!DOCTYPE html>
<html>
<head><title>Leaderboard</title>""" + style + """</head>
<body>
<div class="container">
<h1>🏆 Leaderboard 🏆</h1>
<ol>
{% for s in leaderboard %}
    <li>{{s.name}} - {{s.score}} points - Badges: {{s.badges|length}}</li>
{% endfor %}
</ol>
<a href="/menu">⬅ Back to Menu</a>
</div>
</body>
</html>
"""

# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template_string(index_html)

@app.route("/set_name", methods=["POST"])
def set_name():
    name = request.form["name"]
    session["name"] = name
    if name not in students:
        students[name] = {"score": 0, "badges": []}
    return redirect(url_for("menu"))

@app.route("/menu")
def menu():
    name = session.get("name")
    badges = students.get(name, {}).get("badges", [])
    return render_template_string(menu_html, name=name, badges=badges)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    name = session.get("name")
    if request.method == "POST":
        score = 0
        for i in range(len(quiz_questions)):
            ans = request.form.get(f"q{i}")
            if ans and ans.strip().lower() == quiz_questions[i]["answer"].lower():
                score += 10
        students[name]["score"] = score
        # update leaderboard
        for entry in leaderboard:
            if entry["name"] == name:
                entry["score"] = score
                entry["badges"] = students[name]["badges"]
                break
        else:
            leaderboard.append({"name": name, "score": score, "badges": students[name]["badges"]})
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        return f"<div class='container'><h1>Quiz Completed! Score: {score}</h1><a href='/menu'>⬅ Back to Menu</a></div>"
    return render_template_string(quiz_html, questions=quiz_questions, name=name)

@app.route("/challenge", methods=["GET", "POST"])
def challenge():
    name = session.get("name")
    if request.method == "POST":
        challenge_done = request.form["challenge"]
        if challenge_done not in students[name]["badges"]:
            students[name]["badges"].append(challenge_done)
            for s in leaderboard:
                if s["name"] == name:
                    s["badges"] = students[name]["badges"]
        return redirect(url_for("menu"))
    ch = random.choice(eco_challenges)
    return render_template_string(challenge_html, challenge=ch)

@app.route("/carbon", methods=["GET", "POST"])
def carbon():
    result = None
    if request.method == "POST":
        electricity = float(request.form["electricity"])
        travel = float(request.form["travel"])
        result = (electricity * 0.5) + (travel * 0.2)
    return render_template_string(carbon_html, result=result)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    response = None
    if request.method == "POST":
        question = request.form["question"]
        for key in ai_responses:
            if key in question.lower():
                response = ai_responses[key]
                break
        if not response:
            response = "Sorry, I don't know the answer yet. Try another question."
    return render_template_string(chat_html, response=response)

@app.route("/leaderboard")
def show_leaderboard():
    return render_template_string(leaderboard_html, leaderboard=leaderboard)

# ----------------------------
# Run Server
# ----------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
