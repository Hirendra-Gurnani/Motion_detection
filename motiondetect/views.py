from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import datetime
import time
import MySQLdb as mdb
import cv2
import os
from PIL import Image
# import numpy as np
from django.utils.datastructures import MultiValueDictKeyError
import requests
import json
import uuid
import base64
from PIL import Image
import img2pdf
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# from win32com.client import Dispatch
# import pyttsx3
# speak=Dispatch("SAPI.SpVoice")
# Create your views here.
# def home(req):
# 	return render(req,"home.html")


def admin(req):
    return render(req, 'admin.html')


def a_signup(req):
    return render(req, 'a_signup.html')


def a_logout(req):
    return render(req, 'signin.html')


def a_delete(req):
    email = req.GET['delete']
    con = mdb.connect("localhost", "root", "", "motiondetect")
    cur = con.cursor()
    q = "DELETE from signup WHERE emailad='%s'" % email
    res = cur.execute(q)
    con.commit()
    con.close()
    if res:
        return redirect('a_home')
    else:
        return render(req, 'a_home.html')


def a_home(req):
    users = dict()
    con = mdb.connect("localhost", "root", "", "motiondetect")
    cur = con.cursor()
    q = "SELECT username,emailad from signup"
    cur.execute(q)
    rows = cur.fetchall()
    for user, email in rows:
        users.update({email: user})
    print(users)
    con.commit()
    con.close()
    return render(req, 'a_home.html', {'users': users})


def admin_signup(req):
    if req.method == 'POST':
        email = req.POST['email']
        passwrd = req.POST['password']
        cpass = req.POST['pass']
        con = mdb.connect("localhost", "root", "", "admin")
        cur = con.cursor()
        q = "SELECT aemail from admin1 where aemail='%s'" % email
        result = cur.execute(q)
        if result:
            messages.info(req, "email already exists")
        elif passwrd == cpass:
            con = mdb.connect("localhost", "root", "", "admin")
            cur = con.cursor()
            q = "INSERT into admin1(aemail,password) values('%s','%s')" % (
                email, passwrd)
            out = cur.execute(q)
            if out:
                messages.info(req, "created")
            else:
                messages.info(req, "try again")
            con.commit()
            con.close()
    return render(req, 'admin.html')


def admin_auth(req):
    if req.method == 'POST':
        email = req.POST['email']
        passwrd = req.POST['password']
        con = mdb.connect("localhost", "root", "", "admin")
        cur = con.cursor()
        q = "SELECT password,aemail from admin1 where aemail='%s'" % email
        cur.execute(q)
        rows = cur.fetchall()
        for password, email in rows:
            row = ''.join(password)  # tuple to string
            print(row)
            if row == passwrd:
                return redirect('a_home')
                break
        else:
            messages.info(req, "Invalid Credentials")
            return redirect('admin')
        cur.close()
        con.close()
    else:
        return render(req, 'a_home.html')


def second(req):
    return render(req, 'second.html')


def start(req):

    con = mdb.connect("localhost", "root", "", "motiondetect")
    cur = con.cursor()
    json_file_path = 'C:/Users/ghire/Desktop/motionDetection/static/json/condition.json'

    if not os.path.exists(json_file_path):
        data = {"wait_condition": True}
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file)
    else:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            data['wait_condition'] = True

        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file)

    count = 0
    cap = cv2.VideoCapture(2)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    while cap.isOpened():
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(
            dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < 2000:
                continue
            cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # improve this
            if count >= 20:
                count = 0
                today_date = datetime.date.today()
                today_time = datetime.datetime.now().strftime("%H:%M:%S.%f")
                face = frame1
                filename = str(uuid.uuid4())
                file_path = 'C:/Users/ghire/Desktop/motionDetection/static/images/'+filename+'.jpg'
                # saving imgs

                cv2.imwrite(file_path, face)  # saving
            #     # Provide the path to the image you want to convert

                rec_imgs = filename + '.jpg'
                q = "INSERT into detectmotion(images,dated,timed) values('%s','%s','%s')" % (
                    rec_imgs, today_date, today_time)
                cur.execute(q)
                print("motion detected")
                # Specify the path to the JSON file
                json_file_path = 'C:/Users/ghire/Desktop/motionDetection/static/json/condition.json'

                # Read the JSON file
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)
                    if data["wait_condition"]:
                        sender_email = "ghiren20@gmail.com"
                        sender_password = "G54ZIYfbspC78WNS"
                        recipient_email = "ghiren20@gmail.com"
                        subject = "Motion Detected"
                        message = "<strong style='color: red; font-size: 30px;'>Motion detected on your camera, Kindly refer the Image. Please dial 100 for any emergency.</strong>"
                        image_path = file_path
                        img_name = rec_imgs
                        thread1 = threading.Thread(target=send_email, args=(
                            sender_email, sender_password, recipient_email, subject, message, image_path, img_name))
                        thread1.start()
                        thread2 = threading.Thread(
                            target=wait_for_mail, args=())
                        thread2.start()

            cv2.putText(frame1, "Status:{}".format('Movement'),
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            count += 1

        cv2.imshow("frame", frame1)
        frame1 = frame2
        et, frame2 = cap.read()
        if cv2.waitKey(1) == 27:
            break
    con.commit()
    con.close()
    cv2.destroyAllWindows()
    cap.release()
    return render(req, 'stop.html', {'stop': "Motion Detection Stopped. Mail Sent!",'check_details': "Check Details for more info"})


def wait_for_mail():
    print("Waiting for cooldown")
    # Specify the path to the JSON file
    json_file_path = 'C:/Users/ghire/Desktop/motionDetection/static/json/condition.json'

    # Check if the JSON file exists
    if not os.path.exists(json_file_path):
        # Create a new JSON file with initial values
        data = {"wait_condition": False}
        with open(json_file_path, 'w') as json_file:
            json.dump(data, json_file)

    # Read the JSON file
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Change the value of wait_condition to False
    data['wait_condition'] = False

    # Write the updated data to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    # Wait for 10 seconds
    time.sleep(10)

    # Change the value of wait_condition to True
    data['wait_condition'] = True

    # Write the updated data to the JSON file again
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file)


def send_email(sender_email, sender_password, recipient_email, subject, message, image_path, img_name):
    print("sending mail")
    # Create a multipart message and set its headers
    email_message = MIMEMultipart()
    email_message["From"] = sender_email
    email_message["To"] = recipient_email
    email_message["Subject"] = subject

    # Add the message to the body of the email
    email_message.attach(MIMEText(message, "plain"))

    # Open the image file
    with open(image_path, "rb") as image_file:
        image = MIMEImage(image_file.read())
        # Add a content ID to the image
        image.add_header("Content-Disposition",
                         f"attachment; filename= {img_name}")
        # Attach the image to the email
        email_message.attach(image)

    # Create a secure connection with the SMTP server
    with smtplib.SMTP_SSL("smtp-relay.sendinblue.com", 465) as server:
        # Log in to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email,
                        email_message.as_string())


def stop(req):
    return render(req, 'second.html')


def image_to_pdf(image_path, output_pdf_path):
    with open(output_pdf_path, "wb") as pdf_file:
        image_data = open(image_path, "rb").read()
        pdf_file.write(img2pdf.convert(image_data))

    with open(output_pdf_path, "rb") as file:
        attachment_content = file.read()
        base64_data = base64.b64encode(attachment_content)
        base64_string = base64_data.decode("utf-8")
        return base64_string

    # print(f"Image converted and saved as PDF: {pdf_path}")


def details(req):
    details = dict()
    details2 = dict()
    con = mdb.connect("localhost", "root", "", "motiondetect")
    cur = con.cursor()
    q = "SELECT * FROM detectmotion"

    cur.execute(q)
    rows = cur.fetchall()
    print(rows)
    for row in rows:
        details2 = dict()
        details2[row[2]] = row[0]
        if row[1] in details:
            details[row[1]][row[2]] = row[0]
            pass
        else:
            details[row[1]] = details2

    con.commit()
    con.close()
    return render(req, 'details.html', {'details': details})


def deleted(req):
    dele = req.GET['delet']
    fd = 'C:/Users/ghire/Desktop/motionDetection/static/images/'+str(dele)
    os.remove(fd)
    con = mdb.connect("localhost", "root", "", "motiondetect")
    cur = con.cursor()
    q = "DELETE FROM detectmotion WHERE images='%s'" % dele

    cur.execute(q)
    con.commit()
    con.close()

    return redirect("details")


def signin(req):
    return render(req, "signin.html")


def signup(req):
    return render(req, "signup.html")


def register(req):
    if req.method == 'POST':
        user_name = req.POST['user_name']
        email = req.POST['email']
        passwrd = req.POST['password']
        cpass = req.POST['pass']
        con = mdb.connect("localhost", "root", "", "motiondetect")
        cur = con.cursor()
        q = "SELECT emailad from signup where emailad='%s'" % email
        result = cur.execute(q)
        if result:
            messages.info(req, "Email already exists")
        elif passwrd == cpass:
            con = mdb.connect("localhost", "root", "", "motiondetect")
            cur = con.cursor()
            q = "INSERT into signup(username,emailad,password) values('%s' ,'%s','%s')" % (
                user_name, email, passwrd)
            out = cur.execute(q)
            if out:
                messages.info(req, "created")
            else:
                messages.info(req, "try again")
            con.commit()
            con.close()
    return render(req, 'signin.html')


def login_auth(req):
    if req.method == 'POST':
        email = req.POST['email']
        passwrd = req.POST['password']
        con = mdb.connect("localhost", "root", "", "motiondetect")
        cur = con.cursor()
        q = "SELECT password,username from signup where emailad='%s'" % email
        cur.execute(q)
        rows = cur.fetchall()
        for password, username in rows:
            row = ''.join(password)  # tuple to string
            print(row)
            if row == passwrd:
                # req.session['email']=email
                return render(req, 'second.html')
                break
        else:
            messages.info(req, "Invalid Credentials")
            return redirect('signin')
        cur.close()
        con.close()
    else:
        return render(req, 'second.html')


def setting(req):
    val = ""
    val = req.GET['setting']
    print(val)
    if val == "logout":
        return render(req, "signin.html")
    elif val == "change":
        return render(req, "changepass.html")


def changepass(req):
    if req.method == 'POST':
        current = req.POST["cpass"]
        new = req.POST["npass"]
        con = mdb.connect("localhost", "root", "", "motiondetect")
        cur = con.cursor()
        q = "SELECT password from signup where password='%s'" % current
        cur.execute(q)
        rows = cur.fetchall()
        if (rows):
            q = "UPDATE signup SET password='%s' WHERE password='%s'" % (
                new, current)
            cur.execute(q)
            messages.info(req, "Password Changed")

        else:
            messages.info(req, "Invalid Credentials")
            return redirect('changepass')
        cur.close()
        con.close()
    return render(req, "changepass.html")
