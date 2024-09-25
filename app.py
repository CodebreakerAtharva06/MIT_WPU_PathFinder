from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
import os
import subprocess
import sys

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.root_path + '/static/', filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_pygame', methods=['POST'])
def run_pygame():
    input_method = request.form.get('input_method', 'type')
    os.environ['INPUT_METHOD'] = input_method
    
    # Run the Pygame script
    pygame_process = subprocess.Popen([sys.executable, 'pygame_pathfinding.py'])
    
    return jsonify(status='success', message=f'Pygame started with {input_method} input method')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question', '')
    answer = get_response(question.lower())
    return jsonify(answer=answer)

def get_response(question):
    if "library" in question and "where" in question:
        return "The library is located in the Agastya building."
    elif "cafeteria" in question and "where" in question:
        return "The cafeteria is located between the Dhruv and Kashyap buildings on the second floor."
    elif "gym" in question and "where" in question:
        return "The gym is in Building Chanakya"
    elif "administration office" in question and "where" in question:
        return "The administration office is in Dhruv, room 103."
    elif "student center" in question and "where" in question:
        return "The student center is located at Maitri building ground floor."
    elif "bookstore" in question and "where" in question:
        return "The bookstore is on the ground floor of Agastya building."
    elif "parking" in question and "where" in question:
        return "The main parking lot is located near Vaishishta Building."
    elif "bus stop" in question and "where" in question:
        return "The main bus stop is in front of the Student Center."
    elif "wifi" in question and "password" in question:
        return "The campus WiFi password is 'CampusNet2023'. Please keep it confidential."
    elif "library hours" in question:
        return "The library is open from 8 AM to 10 PM on weekdays, and 10 AM to 6 PM on weekends."
    elif "cafeteria hours" in question:
        return "The cafeteria is open from 7 AM to 8 PM on weekdays, and 9 AM to 6 PM on weekends."
    elif "gym hours" in question:
        return "The gym is open from 6 AM to 10 PM every day."
    elif "lost and found" in question:
        return "The lost and found is located at the Security Office in Building D."
    elif "computer lab" in question and "where" in question:
        return "The computer lab is on the second floor room 204, of Dhruv Building."
    elif "printing" in question:
        return "Printing services are available in the library and the computer lab."
    elif "counseling services" in question:
        return "Counseling services are available in the Health Center, Maitri Building."
    elif "career center" in question:
        return "The Career Center is located on the second floor of the Student Center."
    elif "atm" in question:
        return "ATMs are located on ground floor of Saraswati Vishwa B Building."
    elif "medical center open" in question:
        return "The medical center is open on weekends from 9 AM to 3 PM."
    else:
        return "I'm sorry, I didn't understand that. Can you please ask about a specific place or service on campus?"
if __name__ == '__main__':
    print(f"Static folder path: {app.static_folder}")
    app.run(debug=True)