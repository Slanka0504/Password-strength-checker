from flask import Flask, render_template, request, jsonify
import re
import math
from datetime import timedelta

app = Flask(__name__)

def estimate_cracking_time(password):
    # Character set assumptions
    char_sets = {
        'lower': 26,    # a-z
        'upper': 26,    # A-Z
        'digits': 10,   # 0-9
        'special': 32   # Common special chars
    }
    
    # Determine which character sets are used
    used_sets = 0
    if re.search(r'[a-z]', password):
        used_sets += char_sets['lower']
    if re.search(r'[A-Z]', password):
        used_sets += char_sets['upper']
    if re.search(r'[0-9]', password):
        used_sets += char_sets['digits']
    if re.search(r'[^a-zA-Z0-9]', password):
        used_sets += char_sets['special']
    
    # Calculate combinations (charset^length)
    length = len(password)
    combinations = used_sets ** length
    
    # Assume 1 trillion guesses per second (modern GPU)
    guesses_per_second = 1e12
    
    # Calculate time in seconds
    seconds = combinations / guesses_per_second
    
    # Convert to human-readable time
    if seconds < 1:
        return "instantly"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds/86400)} days"
    else:
        years = seconds / 31536000
        if years > 1000000:
            return "more than 1 million years"
        return f"{int(years)} years"

def check_password_strength(password):
    strength = 0
    feedback = []
    
    # Length check
    if len(password) >= 12:
        strength += 2
        feedback.append("✅ Good length (12+ characters)")
    elif len(password) >= 8:
        strength += 1
        feedback.append("⚠️ Medium length (8-11 characters)")
    else:
        feedback.append("❌ Too short (min 8 characters)")
    
    # Character diversity checks
    checks = [
        (r'[A-Z]', "uppercase letter"),
        (r'[a-z]', "lowercase letter"),
        (r'[0-9]', "number"),
        (r'[^A-Za-z0-9]', "special character")
    ]
    
    for pattern, description in checks:
        if re.search(pattern, password):
            strength += 1
            feedback.append(f"✅ Contains {description}")
        else:
            feedback.append(f"❌ Missing {description}")
    
    # Determine strength level
    if strength >= 6:
        level = "Very Strong"
        color = "green"
    elif strength >= 4:
        level = "Strong"
        color = "lightgreen"
    elif strength >= 3:
        level = "Medium"
        color = "orange"
    else:
        level = "Weak"
        color = "red"
    
    cracking_time = estimate_cracking_time(password)
    
    return {
        "strength_level": level,
        "color": color,
        "feedback": feedback,
        "cracking_time": cracking_time
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    password = request.form.get('password', '')
    if not password:
        return jsonify({"error": "No password provided"})
    
    result = check_password_strength(password)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
