from flask import (Flask, render_template, request, url_for, Response)
import explorerhat as eh
import threading, time
from camera import VideoCamera
import webcamModule as wM
import dataCollectionModule as dcM

app = Flask(__name__)

def start_recording():
    global recordSelection
    while True:
        if recordSelection == 1:
            img = wM.getImg(False,size=[240,120])
            dcM.saveData(img, leftMotor, rightMotor)          
        elif recordSelection == 2:
            dcM.saveLog()
            recordSelection = 0

recordSelection = 0
leftMotor = 0
rightMotor = 0

@app.route("/")
def index():  
    return render_template(
        "index.html"
    )

@app.route("/record")
def record():
    global recordSelection
    recordSelection = int(request.args.get("r"))
    if recordSelection == 0:
        recordSelection = 2
    print(recordSelection)
    return "ok"


@app.route("/motor")
def motor():
    global leftMotor
    global rightMotor   
    leftMotor = int(request.args.get("l"))
    rightMotor = int(request.args.get("r"))
    if leftMotor > 0:
        eh.motor.two.forwards(leftMotor)
    else:
        eh.motor.two.backwards(abs(leftMotor))

    if rightMotor > 0:
        eh.motor.one.forwards(rightMotor)
    else:
        eh.motor.one.backwards(abs(rightMotor))
    print("left motor: {}, right motor: {}".format(leftMotor, rightMotor))
    return "ok"

# live video feed
def gen(camera):
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n' 
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    x = threading.Thread(target=start_recording, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)