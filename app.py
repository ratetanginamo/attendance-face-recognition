from flask import Flask, render_template, Response, request
import cv2, sqlite3, os, datetime

app = Flask(__name__)
camera = cv2.VideoCapture(0)

# Create database if not exists
conn = sqlite3.connect('database/attendance.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS attendance
             (name TEXT, time TEXT)''')

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/mark', methods=['POST'])
def mark():
    name = request.form['name']
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO attendance VALUES (?, ?)", (name, time))
    conn.commit()
    return "Marked attendance for " + name

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
