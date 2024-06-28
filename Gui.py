import tkinter as tk    
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import cv2
import boto3
import os
import sys
from tempfile import gettempdir
from contextlib import closing #it opens the mp3 and closes helps in handling of closing 


my_window = tk.Tk() #This is to create tkinter window  
my_window.geometry("400x450")
my_window.title("Textify")
l1 = tk.Label(my_window, text = "Welcome To Textify!", width=30, font=('times',18, 'bold'))
l1.pack()
b1 = tk.Button(my_window, text="Upload", width=30, command=lambda:upload_Image())
b1.pack()


def upload_Image():
    aws_mgmt_console = boto3.session.Session(profile_name = 'Dacron')
    client = aws_mgmt_console.client(service_name = 'textract' ,region_name = 'ap-south-1')
    global img 
    file_types = [("Image files", "*.png;*.jpg;*.jpeg")]
    fileName = filedialog.askopenfilename(filetype=file_types)   
    img = Image.open(fileName)
    #Image Resizing and displaying
    img_resized = img.resize((400,200))
    img = ImageTk.PhotoImage(img_resized)
    global Image_Path 
    Image_Path = fileName
    imagebytes = get_image_byte(fileName)
    b2 = tk.Button(my_window, image = img)
    b2.pack()
    str_for_polly = ""
    
    response = client.detect_document_text(
    Document={
        'Bytes':imagebytes })
    
    for item in response['Blocks']:
        if item['BlockType'] == 'WORD':
            print(item['Text']) 
            str_for_polly += item['Text'] + " "

    print(str_for_polly)   

    #Code For AWS POLLY
    client2 = aws_mgmt_console.client(service_name = 'polly' ,region_name = 'ap-south-1')
    response_polly = client2.synthesize_speech(Text= str_for_polly, Engine='standard', OutputFormat='mp3', VoiceId='Aditi')
    if 'AudioStream' in response_polly:
        with closing(response_polly['AudioStream']) as stream:
            output = os.path.join(gettempdir(), "speech.mp3")
            try:
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)
                sys.exit(-1)
    else:
        print("No Audio is detected")
        sys.exit(-1)
    
    if sys.platform == 'win32':
        os.startfile(output)


   

def get_image_byte(filename):
    with open(filename, 'rb') as imagefile:
        return imagefile.read() 



my_window.mainloop()