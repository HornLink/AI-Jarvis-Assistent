# This server.py file is server to use this project anywhere like Mobile app, Web browser, Desktop app, etc.
# Press ctrl+f and search "Change this" for required changes while installing the project

from flask import Flask, render_template, Response
import cv2
import threading
import speech_recognition as sr
import pyttsx3 as pt3
import google.generativeai as genai
import datetime
import requests
from pytesseract import pytesseract as td
from dotenv import load_dotenv
import os
load_dotenv()


# Change this: change this Variables:-
assistant_Name = "Jarvis" # you can change assistant name as you want
genai_api_key = os.getenv("GENAI_API_KEY") # replace with your own google's genai api key
weather_app_id = os.getenv("WEATHER_APP_ID") # replace with your own open weather map api key
cascade_path = 'C:\\Users\\tejas\\GitHub\\Augmented_Reality_Assistant\\haarcascade_frontalface_default.xml' # replace with your own haarcascade_frontalface_default.xml path
tesseract_path = "C:\\Users\\tejas\\GitHub\\Augmented_Reality_Assistant\\Tesseract-OCR\\tesseract.exe" # replace with your own tesseract.exe path
external_camera = 'http://192.168.246.140:8080/video' # remove this line if you dont have an external camera
laptop_camera = 0
camera = laptop_camera

app = Flask(__name__)

genai.configure(api_key = genai_api_key)

#location
location_data = requests.get('http://ipinfo.io').json()
city = location_data['city']
region = location_data['region']
loc = str(f"Loc: {city}, {region}")
coordinates = str(f"Coordinates: {location_data['loc']}")

#weather program
response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_app_id}")
data = response.json ()
temp = "Temperature: " + str(int(data["main"]["temp"]-273.15)) + "c"



#face detection
face_cascade = cv2.CascadeClassifier(cascade_path)

#text detection
td.tesseract_cmd = tesseract_path


# graphical program condition
frame_design = True
caption = True
mic_animation = False
internet_connection_status = False
internet_connection_animation = True
time = True
weather = True
location = True
caption = ""
rectangle_program = False

google_recognize_server_connection = False
genai_server_connection = False


# graphical public variables
frame = None
main_frame = None
td_x, td_y, td_w, td_h = None, None, None, None
fd_x, fd_y, fd_w, fd_h = None, None, None, None
     
def display():
    global frame
    global main_frame

    cap = cv2.VideoCapture(camera)
    font = cv2.FONT_ITALIC

    #Calculation to align item
    def top(percent):
        result = int(percent * height / 100)
        return result

    def left(percent):
        result = int(percent * width / 100)
        return result

    thread4 = threading.Thread(target=text_detection_function)
    thread4.start()

    thread5 = threading.Thread(target=is_connected)
    thread5.start()

    global x,y,w,h

    circle_animation = 0

    RSx = 360
    RSy = 360
    REx = 360
    REy = 360


    while True:
            success, frame = cap.read()
            height, width = frame.shape[:2]

            
            x, y, w, h = left(10), top(20), left(90), top(80)
            obj_size = int((width+height)/3000)+0.8
            obj_strok = int(obj_size*2)+1

            circle_animation+=1
            if circle_animation > 40:
                 circle_animation = 0

            RSx -= 3
            RSy -= 3
            REx += 3
            REy += 3

            if REx > 450:
                RSx = 360
                RSy = 360
                REx = 360
                REy = 360
                 

            if frame_design:
                main_frame = cv2.rectangle(frame, (left(10), top(20)), (left(90), top(80)), (255, 255, 255), 2)
                img = cv2.line(frame, (left(0), top(0)), (left(10), top(20)), (255, 255, 255), 2)
                img = cv2.line(frame, (left(100), top(0)), (left(90), top(20)), (255, 255, 255), 2)
                img = cv2.line(frame, (left(100), top(100)), (left(90), top(80)), (255, 255, 255), 2)
                img = cv2.line(frame, (left(0), top(100)), (left(10), top(80)), (255, 255, 255), 2)

                img = cv2.circle(frame, (left(50),top(50)), 16, (255, 255, 255), 1) 
                img = cv2.line(frame, (left(48), top(50)), (left(52), top(50)), (255, 255, 255), 1)
                img = cv2.line(frame, (left(50), top(47)), (left(50), top(53)), (255, 255, 255), 1)
                

            if caption:
                line1, line2, line3, line4, line5,= caption[0:100], caption[100:200], caption[200:300], caption[300:400], caption[400:500]
                img = cv2.putText(frame, line1, (left(11), top(85)), font, 0.7, (255,255,255), 1, cv2.LINE_AA)
                img = cv2.putText(frame, line2, (left(11), top(88)), font, 0.7, (255,255,255), 1, cv2.LINE_AA)
                img = cv2.putText(frame, line3, (left(11), top(91)), font, 0.7, (255,255,255), 1, cv2.LINE_AA)
                img = cv2.putText(frame, line4, (left(11), top(94)), font, 0.7, (255,255,255), 1, cv2.LINE_AA)
                img = cv2.putText(frame, line5, (left(11), top(97)), font, 0.7, (255,255,255), 1, cv2.LINE_AA)


            if mic_animation:
                img = cv2.rectangle(frame, (left(4), top(69)), (left(7), top(75)), (255, 255, 255), 2)
                img = cv2.line(img, (left(5.5), top(75)), (left(5.5), top(78)), (255, 255, 255), 2)
                img = cv2.line(img, (left(4), top(78)), (left(7), top(78)), (255, 255, 255), 2)

            if internet_connection_animation:
                cv2.circle(img, (left(95), top(30)), 40, (255, 255, 255), 2)
                if internet_connection_status:
                    if google_recognize_server_connection:
                        cv2.circle(img, (left(94), top(32)), 1, (0, 0, 255), 2)
                    if genai_server_connection:
                        cv2.circle(img, (left(96), top(28)), 1, (0, 0, 255), 2)
                    cv2.circle(img, (left(95), top(30)), circle_animation, (255, 255, 255), 2)
                    cv2.circle(img, (left(95), top(30)), 1, (255, 255, 255), 2)
                else:
                    cv2.putText(frame, "X", (left(93.2), top(33.7)), font, obj_size*3, (0,0,255), obj_strok*2, cv2.LINE_AA)
                
                      

            if location:
                img = cv2.putText(frame, coordinates, (left(10), top(12)), font, obj_size, (255,255,255), obj_strok, cv2.LINE_AA)
                img = cv2.putText(frame, loc, (left(10), top(18)), font, obj_size, (255,255,255), obj_strok, cv2.LINE_AA)

            if time:
                current_time = datetime.datetime.now().time().strftime("%I:%M %p")
                cv2.circle(img, (left(74), top(11)), 20, (255,255,255), 2)
                cv2.line(img, (left(74), top(11)), (left(74), top(10)), (255,255,255), 2)
                cv2.line(img, (left(74), top(11)), (left(74.8), top(11)), (255,255,255), 2)
                img = cv2.putText(frame, current_time, (left(77), top(12)), font,  obj_size, (255,255,255), obj_strok, cv2.LINE_AA)

            if weather:
                img = cv2.putText(frame, temp, (left(73), top(18)), font, obj_size, (255,255,255), obj_strok, cv2.LINE_AA)

            if rectangle_program:
                img = cv2.rectangle(frame, (RSx,RSy), (REx, REy), (255, 255, 255), 2)


            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
def text_detection_function():
    global detected_text
    while True:
        try:
            text_in_image = td.image_to_string(main_frame[y:h, x:w])
            if text_in_image != "":
                detected_text = text_in_image
                print(detected_text)

        except:
             pass
        
def is_connected():
    global internet_connection_status
    while True:
        try:
            requests.get("https://www.google.com",timeout=1)
            internet_connection_status = True
        except:
            internet_connection_status = False


#Asssistant

user_input = ""
detected_text = ""

def ai_response(user_input):
    global genai_server_connection
    try:
        
        model = genai.GenerativeModel('models/gemini-pro')
        genai_server_connection = True
        response = model.generate_content(user_input).text.replace("*", "")
        genai_server_connection = False
        return response
    except:
        return "I am sorry, for some reason i am not able to give you an answer"

def Vinput():
        global mic_animation
        global google_recognize_server_connection
        try:
            mic_animation = True
            R = sr.Recognizer()
            with sr.Microphone(1) as source:
                google_recognize_server_connection = True
                value = R.recognize_google(R.listen(source))
                google_recognize_server_connection = False
                mic_animation = False
                return value

        except sr.UnknownValueError:
            mic_animation = False
            value =""
            return value
        
        except:
            mic_animation = False
            if not internet_connection_status:
                value ="You are not connected to the internet. I am unable to access information."
            else:
                value =""
            return value


def assistantProgram():
        assistant = pt3.init()
        assistant.say('what can i help you')
        assistant.runAndWait()
        global time
        global weather
        global caption
        global rectangle_program

        while True:
            user_input = Vinput()
            print(user_input)
            if user_input=="":
                pass
            elif "what is your name" in user_input or\
                 "who are you" in user_input or\
                 "tell me your name" in user_input:
                 assistant.say("i am "+assistant_Name)
                 assistant.runAndWait()

            #time program
            elif "start time program" in user_input or\
                 "turn on time program" in user_input:
                    time = True
                    assistant.say("starting time program")
                    assistant.runAndWait()
            elif "turn off time program" in user_input or\
                 "close time program" in user_input:
                    time = False
                    assistant.say("Closing time program")
                    assistant.runAndWait()

            #weather program
            elif "start weather program" in user_input or\
                "turn on weather program" in user_input:
                 weather = True
                 assistant.say("starting weather program")
                 assistant.runAndWait()
            elif "turn off weather program" in user_input or\
                 "turn off leather program" in user_input or\
                 "turn off veda program" in user_input or\
                 "turn off feather program" in user_input or\
                 "turn off whether program" in user_input or\
                    "close weather program" in user_input:
                    weather = False
                    assistant.say("Closing weather program")
                    assistant.runAndWait()

            #text detection and explaination
            elif "detected text" in user_input or\
                 "meaning of this text" in user_input or\
                 "meaning of this detected text" in user_input:
                    caption = str(ai_response("tell me in 3 lines what is the meaning of"+detected_text))
                    print(caption)
                    assistant.say("in detected text"+caption)
                    assistant.runAndWait()
                    caption = ""

            #rectangle program
            elif "turn on rectangle program" in user_input or\
                 "on rectangle program" in user_input or\
                 "start rectangle program" in user_input:
                    rectangle_program = True
                    assistant.say("starting rectangle program")
                    assistant.runAndWait()
                
            elif "turn off rectangle program" in user_input or\
                 "off rectangle program" in user_input or\
                 "close rectangle program" in user_input:
                    rectangle_program = False
                    assistant.say("closing rectangle program")
                    assistant.runAndWait()
            

            else:
                caption = str(ai_response("tell me in 3 lines"+user_input))
                print(caption)
                assistant.say(caption)
                assistant.runAndWait()
                caption = ""

def call_assistant():
    while True:
        user_input = Vinput()
        if assistant_Name in user_input:
            assistantProgram()
        else:
            print(user_input)




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(display(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    thread1 = threading.Thread(target=display)
    thread1.start()

    thread2 = threading.Thread(target=call_assistant)
    thread2.start()


    app.run(host="127.0.0.1", port=5000)