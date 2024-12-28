# This Project.py file is the main project file, you can run this project on your desktop by running this file.
# Press ctrl+f and search "Change this" for required changes while installing the project

import cv2
from cvzone.HandTrackingModule import HandDetector
import threading
import pyttsx3 as pt3
import speech_recognition as sr
import google.generativeai as genai
import datetime
import requests
import webbrowser
from pytesseract import pytesseract as td
import pygame
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize pygame mixer
pygame.mixer.init()

# Change this: change this Variables:-
assistant_Name = "Jarvis" # you can change assistant name as you want
genai_api_key = os.getenv("GENAI_API_KEY") # replace with your own google's genai api key
weather_app_id = os.getenv("WEATHER_APP_ID") # replace with your own open weather map api key
cascade_path = 'C:\\Users\\tejas\\GitHub\\Augmented_Reality_Assistant\\haarcascade_frontalface_default.xml' # replace with your own haarcascade_frontalface_default.xml path
tesseract_path = "C:\\Users\\tejas\\GitHub\\Augmented_Reality_Assistant\\Tesseract-OCR\\tesseract.exe" # replace with your own tesseract.exe path
external_camera = os.getenv("EXTERNAL-CAMERA") # replace with your own external camera path, if you don't have external camera then remove this line
laptop_camera = 0
camera = laptop_camera
detector = HandDetector(detectionCon=0.8, maxHands=1)  # Track only one hand

genai.configure(api_key = genai_api_key)

# graphical program ON or OFF
frame_design = True
caption = True
mic_animation = False
internet_connection_status = False
internet_connection_animation = True
time = True
weather = True
location = True
face_detection = True
caption = ""
rectangle_program = False

# Graphical square with Hand Interaction
square = False
draw = False
square_start = (None, None)
square_end = (None, None)

#server connection
google_recognize_server_connection = False
genai_server_connection = False

# graphical public variables
frame = None
main_frame = None
height = width = None
square_frame = None
td_x, td_y, td_w, td_h = None, None, None, None
fd_x, fd_y, fd_w, fd_h = None, None, None, None


#assistant animation

#location
try:
    location_data = requests.get('http://ipinfo.io').json()
    city = location_data['city']
    region = location_data['region']
    loc = str(f"Loc: {city}, {region}")
    coordinates = str(f"Coordinates: {location_data['loc']}")
except Exception as e:
    print(e)
    location = False

#weather program
try:
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_app_id}")
    data = response.json ()
    temp = "Temperature: " + str(int(data["main"]["temp"]-273.15)) + "c"
except Exception as e:
    print(e)
    weather = False


#face detection
face_cascade = cv2.CascadeClassifier(cascade_path)

#text detection
td.tesseract_cmd = tesseract_path

def wrap_text(text, max_width, font, font_size, thickness):
    """Split text into lines that fit within max_width pixels"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Get size of current line with test word added
        line_text = ' '.join(current_line)
        (line_width, _) = cv2.getTextSize(line_text, font, font_size, thickness)[0]
        
        if line_width > max_width:
            # Remove last word and add current line
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add final line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines[:5]  # Limit to 5 lines maximum

     
def display():
    global frame, main_frame, square_frame, height, width

    cap = cv2.VideoCapture(camera)
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', (1000, 500))
    font = cv2.FONT_ITALIC

    play_sound("Sound-Effects/jarvis-start.mp3")

    #Calculation to align item
    def top(percent):
        result = int(percent * height / 100)
        return result

    def left(percent):
        result = int(percent * width / 100)
        return result

    
    thread3 = threading.Thread(target=face_detection_function)
    thread3.start()

    thread4 = threading.Thread(target=text_detection_function)
    thread4.start()

    thread5 = threading.Thread(target=is_connected)
    thread5.start()

    thread6 = threading.Thread(target=hand_tracking)
    thread6.start()


    global x,y,w,h
    x = None

    circle_animation = 0

    RSx = 260
    RSy = 260
    REx = 260
    REy = 260

    obj_size = obj_strok = None

    while True:
            success, frame = cap.read()
            if height is None:
                height, width = frame.shape[:2]
            
            if x is None:
                x, y, w, h = left(10), top(20), left(90), top(80)

            if obj_strok is None:
                obj_size = round((width+height)/3000, 1)
                obj_strok = round(obj_size*2)

            if internet_connection_status:
                circle_animation+=1
                if circle_animation > round(obj_size*65):
                    circle_animation = 0

            if rectangle_program:
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
                main_frame = cv2.rectangle(frame, (left(10), top(20)), (left(90), top(80)), (255, 0, 0), obj_strok)
                img = cv2.line(frame, (left(0), top(0)), (left(10), top(20)), (255, 0, 0), obj_strok)
                img = cv2.line(frame, (left(100), top(0)), (left(90), top(20)), (255, 0, 0), obj_strok)
                img = cv2.line(frame, (left(100), top(100)), (left(90), top(80)), (255, 0, 0), obj_strok)
                img = cv2.line(frame, (left(0), top(100)), (left(10), top(80)), (255, 0, 0), obj_strok)

                img = cv2.circle(frame, (left(50),top(50)), round(obj_size*20), (255, 0, 0), obj_strok) 
                img = cv2.line(frame, (left(48), top(50)), (left(52), top(50)), (255, 0, 0), obj_strok)
                img = cv2.line(frame, (left(50), top(47)), (left(50), top(53)), (255, 0, 0), obj_strok)
                

            if caption:
                # Calculate maximum width based on frame size
                max_text_width = int(width * 0.80)  # Use 80% of frame width
                
                # Get wrapped lines
                lines = wrap_text(caption, max_text_width, font, obj_size, obj_strok)
                
                # Draw each line
                for i, line in enumerate(lines):
                    y_pos = top(85 + (i * 3))  # Increment y position for each line
                    img = cv2.putText(frame, line, (left(11), y_pos), font, obj_size, 
                                     (255,255,255), obj_strok, cv2.LINE_AA)

            if mic_animation:
                img = cv2.rectangle(frame, (left(4), top(69)), (left(7), top(75)), (255, 0, 0), obj_strok)
                img = cv2.line(img, (left(5.5), top(75)), (left(5.5), top(78)), (255, 0, 0), obj_strok)
                img = cv2.line(img, (left(4), top(78)), (left(7), top(78)), (255, 0, 0), obj_strok)

            if internet_connection_animation:
                cv2.circle(img, (left(95), top(30)), round(obj_size*65), (255, 0, 0), obj_strok)
                if internet_connection_status:
                    if google_recognize_server_connection:
                        cv2.circle(img, (left(94), top(32)), 1, (0, 0, 255), obj_strok)
                    if genai_server_connection:
                        cv2.circle(img, (left(96), top(28)), 1, (0, 0, 255), obj_strok)
                    cv2.circle(img, (left(95), top(30)), circle_animation, (255, 0, 0), obj_strok)
                    cv2.circle(img, (left(95), top(30)), 1, (255, 0, 0), obj_strok)
                else:
                    cv2.putText(frame, "X", (left(93.3), top(32.5)), font, obj_size*3, (0,0,255), obj_strok, cv2.LINE_AA)     

            if location:
                img = cv2.putText(frame, coordinates, (left(10), top(12)), font, obj_size, (255, 0, 0), obj_strok, cv2.LINE_AA)
                img = cv2.putText(frame, loc, (left(10), top(18)), font, obj_size, (255, 0, 0), obj_strok, cv2.LINE_AA)

            if time:
                current_time = datetime.datetime.now().time().strftime("%I:%M %p")
                cv2.circle(img, (left(74), top(11)), round(obj_size*25), (255, 0, 0), obj_strok)
                cv2.line(img, (left(74), top(11)), (left(74), top(10)), (255, 0, 0), obj_strok)
                cv2.line(img, (left(74), top(11)), (left(74.8), top(11)), (255, 0, 0), obj_strok)
                img = cv2.putText(frame, current_time, (left(77), top(12)), font,  obj_size, (255, 0, 0), obj_strok, cv2.LINE_AA)

            if weather:
                img = cv2.putText(frame, temp, (left(73), top(18)), font, obj_size, (255, 0, 0), obj_strok, cv2.LINE_AA)

            if rectangle_program:
                img = cv2.rectangle(frame, (RSx,RSy), (REx, REy), (255, 0, 0), 2)

            if face_detection:
                try:
                    img = cv2.rectangle(frame, (fd_x,fd_y), (fd_x+fd_w, fd_y+fd_h), (255, 0, 0), obj_strok)
                except:
                    pass

            if square:
                square_frame = cv2.rectangle(frame, square_start, square_end, (255, 225, 225), obj_strok)

                #delete square button
                img = cv2.circle(frame, (left(54), top(9)), round(obj_size*65), (0, 0, 255), obj_strok)
                img = cv2.putText(frame, "x", (left(51.5), top(12)), font, obj_size*5, (0,0,255), obj_strok, cv2.LINE_AA)
                img = cv2.putText(frame, "Delete Rectangle", (left(47), top(18)), font, obj_size, (0,0,255), obj_strok, cv2.LINE_AA)
                 

            cv2.imshow('frame', frame)

            if cv2.waitKey(1) == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()  

def hand_tracking():
     global frame, square, draw, square_start, square_end, detected_text
     while True:
        try:  # Add error handling
            current_frame = frame.copy()  # Create a copy of the frame
            if current_frame is not None:
                hands, img = detector.findHands(current_frame)  # Use the copy instead
                if hands:
                    hand = hands[0]
                    lmList = hand["lmList"]
                    indexFingerTip = lmList[8]  # Index of Index Finger
                    thumbTip = lmList[4]    # Index of Thumb

                    # Draw square if thumbTip & indexFingerTip is touched
                    # if again thumbTip & indexFingerTip is touched check for is the user trying streach the point of the square
                    if draw:
                        # Bottom-right cornor
                        if abs(thumbTip[0] - indexFingerTip[0]) < 20 and abs(thumbTip[1] - indexFingerTip[1]) < 20 and abs(square_end[0] - indexFingerTip[0]) < 25 and abs(square_end[1] - indexFingerTip[1]) < 25:
                            square_end = (indexFingerTip[0] - 10, indexFingerTip[1] - 10)
                            play_sound("Sound-Effects/selection.mp3")

                        # Top-left cornor
                        if abs(thumbTip[0] - indexFingerTip[0]) < 20 and abs(thumbTip[1] - indexFingerTip[1]) < 20 and abs(square_start[0] - indexFingerTip[0]) < 25 and abs(square_start[1] - indexFingerTip[1]) < 25:
                            square_start = (indexFingerTip[0] + 10, indexFingerTip[1] + 10)
                            play_sound("Sound-Effects/selection.mp3")


                        # Top-right cornor
                        if abs(thumbTip[0] - indexFingerTip[0]) < 20 and abs(thumbTip[1] - indexFingerTip[1]) < 20 and abs(square_end[0] - indexFingerTip[0]) < 25 and abs(square_start[1] - indexFingerTip[1]) < 25:
                            square_end = (indexFingerTip[0] - 10, square_end[1])
                            square_start = (square_start[0], indexFingerTip[1] + 10)
                            play_sound("Sound-Effects/selection.mp3")


                        # Bottom-left cornor
                        if abs(thumbTip[0] - indexFingerTip[0]) < 20 and abs(thumbTip[1] - indexFingerTip[1]) < 20 and abs(square_start[0] - indexFingerTip[0]) < 25 and abs(square_end[1] - indexFingerTip[1]) < 25:
                            square_start = (indexFingerTip[0] + 10, square_start[1])
                            square_end = (square_end[0], indexFingerTip[1] - 10)
                            play_sound("Sound-Effects/selection.mp3")

                        if indexFingerTip[0] > int(51 * width / 100) and indexFingerTip[0] < int(57 * width / 100) and indexFingerTip[1] > int(8 * height / 100) and indexFingerTip[1] < int(16 * height / 100):
                            draw = square = False
                            play_sound("Sound-Effects/delete_button.mp3")
                            
                    elif not draw:
                        # create square around Tip Touch
                        if abs(thumbTip[0] - indexFingerTip[0]) < 20 and abs(thumbTip[1] - indexFingerTip[1]) < 20:
                            square = True
                            square_start = (indexFingerTip[0] - 100, indexFingerTip[1] - 25)
                            square_end = (indexFingerTip[0] + 100, indexFingerTip[1] + 25)
                            play_sound("Sound-Effects/selection.mp3")
                        # Fix the square in one place when the user removes fingertip contact.
                        elif square:
                            draw = True

        except Exception as e:
            pass

def text_detection_function():
    global detected_text
    while True:
        try:
            if square:
                # Extract the coordinates of the square
                x1, y1 = square_start
                x2, y2 = square_end

                # Ensure coordinates are within the bounds of the Square Frame
                x1, y1 = max(x1, 0), max(y1, 0)
                x2, y2 = max(x2, 0), max(y2, 0)

                # Extract the region of interest (ROI) from the frame
                square_frame = main_frame[y1:y2, x1:x2]

                # Perform text detection in the Square Frame
                text_in_image = td.image_to_string(square_frame)
            else:
                text_in_image = td.image_to_string(main_frame[y:h, x:w])
            
            if text_in_image != "":
                detected_text = text_in_image
                print(detected_text)

        except:
             pass
        
def is_connected():
    # check for internet connection by Pinging google
    global internet_connection_status
    while True:
        try:
            requests.get("https://www.google.com",timeout=1)
            internet_connection_status = True
        except:
            internet_connection_status = False
        
def face_detection_function():
    global fd_x
    global fd_y
    global fd_w
    global fd_h
    if face_detection:
        while True:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x, y , w ,h) in faces:
                    fd_x = x
                    fd_y = y
                    fd_w = w
                    fd_h = h 
            except:
                pass


def play_sound(sound_file):
    """Play a sound file without blocking"""
    try:
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
    except Exception as e:
        print(f"Error playing sound: {e}")


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
                listen = R.listen(source)
                mic_animation = False
                value = R.recognize_google(listen)
                google_recognize_server_connection = False
                return value

        except sr.UnknownValueError:
            mic_animation = False
            value =""
            return value
        
        except:
            mic_animation = False
            if not internet_connection_status:
                value ="You are not connected to the internet. I am unable to access information."
                play_sound("Sound-Effects/notification.mp3")
            else:
                value =""
            return value


def assistantProgram():
        assistant = pt3.init()
        assistant.setProperty('rate', 180)  # Speed (words per minute)
        assistant.say('at your service sir')
        assistant.runAndWait()
        global time, weather, face_detection, caption, rectangle_program, square, draw, square_start, square_end

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

            #Google Map program
            elif "show me the direction" in user_input or\
                 "show the direction" in user_input:
                    assistant.say("ok, where are you right now")
                    assistant.runAndWait()
                    user_input = Vinput()
                    source = user_input

                    assistant.say("what is your destination")
                    assistant.runAndWait()
                    user_input = Vinput()
                    destination = user_input

                    assistant.say("redirecting to google maps")
                    assistant.runAndWait()

                    url = "https://www.google.com/maps/dir/?api=1&origin={}&destination={}".format(source, destination)
                    webbrowser.open(url)

            #face detection
            elif "start face detection" in user_input or\
                 "turn on face detection" in user_input:
                    face_detection = True
                    assistant.say("starting face detection")
                    assistant.runAndWait()
            elif "close face detection" in user_input or\
                 "turn off face detection" in user_input:
                    face_detection = False
                    assistant.say("closing face detection")
                    assistant.runAndWait()

            #text detection and explaination
            elif "detected text" in user_input or\
                 "meaning of this text" in user_input or\
                 "meaning of this detected text" in user_input:
                    caption = str(ai_response("Give me an answer in one line: What is this "+detected_text))
                    print(caption)
                    square = draw = False
                    square_start = square_end = (None, None)
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
                
            # Generative AI response on user input  
            else:
                caption = str(ai_response("Give me an answer in one line: "+user_input))
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



thread1 = threading.Thread(target=display)
thread1.start()

thread2 = threading.Thread(target=call_assistant)
thread2.start()