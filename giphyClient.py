import giphy_client
from giphy_client.rest import ApiException
from flask import Flask, make_response, request, redirect, url_for, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask import Response
from flask_cors import CORS
import werkzeug
from werkzeug.utils import secure_filename
import os
from os import path
import memeEngine
from memeEngine import prediction_utils
import base64

class giphyQuery:
    def __init__(self, parameter):
        self.parameter = parameter
        self.api_key = ''
        self.api_instance = giphy_client.DefaultApi()

    def returnGifHTML(self):
        fmt = 'json'
        return "<img src=\"" + \
               str((self.api_instance.gifs_random_get(self.api_key, tag=self.parameter, fmt=fmt)
                    ).data.fixed_height_downsampled_url) + "\"/>"

    def returnGifURL(self):
        return (self.api_instance.gifs_random_get(self.api_key, tag=self.parameter, fmt='json')
                ).data.fixed_height_downsampled_url

    def gifSearch(self):
        fmt = 'json'
        response = self.api_instance.gifs_search_get(self.api_key, q=self.parameter, fmt=fmt).data
        return response

    def gifSearchByTag(self):
        response = self.api_instance.gifs_categories_category_tag_get(self.api_key, q=self.parameter, fmt='json').data
        return response

import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import os
import smtplib
import time

class emailSend:
    def __init__(self, toList, subject, message):
        self.toList = toList
        self.subject = subject
        self.message = message
        if type(toList) != list:
            raise AssertionError("To address must be a list")

    def genEmailBody(self):
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = 'Project MEME'
        msg['To'] = 'Recipients'
        body = MIMEText(self.message, 'html')
        msg.attach(body)
        return msg.as_string()

    def sendEmail(self):
        sendServer = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        sendServer.ehlo()
        sendServer.login()
        for i in self.toList:
            sendServer.sendmail('projectmeme.hack@gmail.com', i, self.genEmailBody())
            print("Email sent to", i)
        sendServer.close()

class FetchEmail():
    connection = None
    error = None

    def __init__(self, mail_server, username, password):
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select(readonly=False) # so we can mark mails as read

    def close_connection(self):
        self.connection.close()

    def save_attachment(self, msg, download_folder="/Users/jaspergilley/Documents/ATT Hackathon/meme-hack/resources"):
        att_path = "No attachment found."
        varFrom = msg['From']
        varSubject = msg['Subject']
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
        if varSubject == "Null" or varSubject == "NULL" or varSubject == "null":
            varSubject = ""
        else:
            varSubject = " " + varSubject
        emotion = prediction_utils.prediction_path(att_path)
        varFrom = varFrom.replace("<", "")
        varFrom = varFrom.replace(">", "")
        varFromList = varFrom.split(" ")
        emailSend([varFromList[-1]], "Project MEME Response", """<p><strong>Hi there, {}</strong></p>
<p>We detected your emotion as {}, and your subject line secondary query was {}.</p>
<p>{}</p>""".format(varFromList[0], emotion, varSubject, giphyQuery(emotion + varSubject).returnGifHTML())).sendEmail()
        return att_path

    def fetch_unread_messages(self):
        emails = []
        (result, messages) = self.connection.search(None, 'UnSeen')
        if result == "OK":
            for message in messages[0].split(' '):
                try: 
                    ret, data = self.connection.fetch(message,'(RFC822)')
                except:
                    print("No new emails to read.")
                    self.close_connection()
                    continue

                msg = email.message_from_string(data[0][1])
                if isinstance(msg, str) == False:
                    emails.append(msg)
                response, data = self.connection.store(message, '+FLAGS','\\Seen')

            return emails

        self.error = "Failed to retreive emails."
        return emails

    def parse_email_address(self, email_address):
        """
        Helper function to parse out the email address from the message

        return: tuple (name, address). Eg. ('John Doe', 'jdoe@example.com')
        """
        return email.utils.parseaddr(email_address)


while True:
    instance = FetchEmail()
    emailList = instance.fetch_unread_messages()
    if emailList != []:
        print("email found")
        for i in emailList:
            instance.save_attachment(i)

    time.sleep(10)

#emotion = prediction_utils.prediction_path("/Users/jaspergilley/Dropbox/Project MEME/steven2.png")
#print(emotion)

exit(314)

app = Flask(__name__)
CORS(app)
api = Api(app)

UPLOAD_FOLDER = '/Users/jaspergilley/Documents/ATT Hackathon/meme-hack/memeEngine/saved_images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class HelloWorld(Resource):
    def get(self):
        return Response(giphyQuery("sad dog").returnGifHTML())

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        if request.method == 'POST':
            #print(request.files)
            # check if the post request has the file part
            if 'file' not in request.files:
                print("File not in request.files")
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                print("Filename not found")
                #flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                emotion = prediction_utils.prediction_path(
                    '/Users/jaspergilley/Documents/ATT Hackathon/meme-hack/memeEngine/saved_images/' + file.filename)
                print(emotion)
                return giphyQuery(emotion).returnGifHTML()
        return "success"

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(host='192.168.30.161')
