# Importing the required modules
import tkinter as tk  # graphical user interface toolkit
from tkinter import *
from tkinter import constants
import easygui  # to open the filebox
import cv2  # for image processing
import matplotlib.pyplot as plt
import os  # to read and save path
import sys  #

# Making the GUI main window
root = tk.Tk()

width = 400 # width for the Tk root
height = 420 # height for the Tk root

screen_width = root.winfo_screenwidth() # width of the screen
screen_height = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)

root.title('Cartoonify Your Image!')
root.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + '\\rainbow.ico')
root.geometry('%dx%d+%d+%d' % (width, height, x, y))
root.resizable(False, False)
background_image = PhotoImage(file = os.path.dirname(os.path.realpath(__file__)) + '\\gradient_blue.gif')
background_label = Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

""" fileopenbox opens the box to choose file and help us store file path as string """

image_path = '' # global variable image_path for different types of upload mechanisms

def upload():
    
    image_path_upload = easygui.fileopenbox()
    global image_path
    image_path = image_path_upload
    if image_path_upload is not None:
        cartoonify(image_path_upload)
    else:
        W = "Choose a proper image to cartoonify!"
        tk.messagebox.showinfo(title="Warning!", message=W)

def upload_from_camera():
    
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    image_path_camera_feed = ''

    while TRUE:
        
        ret, frame = camera.read()
        
        if not ret:
            I = "Failed to read frame..."
            tk.messagebox.showinfo(title="Frame Read Failed", message=I)
            break
        
        window_name = "Press SPACE to take a photograph to cartoonify and close the camera application!"
        cv2.imshow(window_name, frame)
        k = cv2.waitKey(1)
        
        if k%256 == 32:
            # SPACE pressed
            current_directory = os.path.dirname(os.path.realpath(__file__))
            image_path_camera_feed = current_directory + "\\photoshoot.png"
            global image_path
            image_path = image_path_camera_feed
            image_name = "photoshoot.png"
            cv2.imwrite(image_name, frame)
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) <1:
            break
    
    camera.release()
    cv2.destroyAllWindows()
    
    if image_path_camera_feed is None or not image_path_camera_feed:
        W = "Take a picture from the camera application!"
        tk.messagebox.showinfo(title="Warning!", message=W)
    else:
        cartoonify(image_path_camera_feed)

# Store the image
def cartoonify(image_path):

    # read image
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    print(original_image)  # this will be stored in form of numbers

    # to confirm it is image that was chosing
    if original_image is None:
        print("Can't find any image. Choose appropriate file")
        sys.exit()
    resize_image1 = cv2.resize(original_image, (960, 540))

    # converting an image to grayscale
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    resize_image2 = cv2.resize(grayscale_image, (960, 540))

    # applying median blur to smoothen an image
    smooth_grayscale_image = cv2.medianBlur(grayscale_image, 5)
    resize_image3 = cv2.resize(smooth_grayscale_image, (960, 540))

    # retrieving the edges for cartoon effect
    # by using thresholding technique
    get_edge = cv2.adaptiveThreshold(smooth_grayscale_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    resize_image4 = cv2.resize(get_edge, (960, 540))

    # applying bilateral filter to remove noise
    # and keep edge sharp as required
    color_image = cv2.bilateralFilter(original_image, 9, 300, 300)
    resize_image5 = cv2.resize(color_image, (960, 540))

    # masking edged image with our "BEAUTIFY" image
    cartoon_image = cv2.bitwise_and(color_image, color_image, mask=get_edge)
    global resize_image6 # must be declared to be reachable outside of the scope
    resize_image6 = cv2.resize(cartoon_image, (960, 540))

    # Plotting all the image transformations
    images = [resize_image1, resize_image2, resize_image3, resize_image4, resize_image5, resize_image6]
    fig, axes = plt.subplots(3, 2, figsize=(8, 8), subplot_kw={'xticks': [], 'yticks': []},
                             gridspec_kw=dict(hspace=0.1, wspace=0.1))
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i], cmap='gray')

    # Show all the image transformations
    plt.show()

def save(resize_image6, image_path):
    # saving an image using imwrite function
    new_name = "cartoonified_" + os.path.basename(image_path)
    original_filepath = os.path.dirname(image_path)
    print(original_filepath)
    path = os.path.join(original_filepath, new_name)
    cv2.imwrite(path, cv2.cvtColor(resize_image6, cv2.COLOR_RGB2BGR))
    I = "Image saved by name " + new_name + " at " + path
    tk.messagebox.showinfo(title="Save Info", message=I)

def close():
    root.destroy()

# Making the Cartoonify button in the GUI main window
upload = Button(root, text="Cartoonify an Image", command=upload, padx=50, pady=10)
upload.configure(background="#374256", foreground="wheat", font=('calibri', 10, 'bold'))
upload.pack(side=TOP, pady=30)

upload_from_camera = Button(root, text="Cartoonify Image from Camera", command=upload_from_camera, padx=20, pady=10)
upload_from_camera.configure(background="#374256", foreground="wheat", font=('calibri', 10, 'bold'))
upload_from_camera.pack(side=TOP, pady=30)

# Making a Save button in the GUI main window
save_button = Button(root, text="Save Cartoonified Image", command=lambda: save(resize_image6, image_path), padx=38, pady=10)
save_button.configure(background='#374256', foreground='wheat', font=('calibri', 10, 'bold'))
save_button.pack(side=TOP, pady=30)

close_button = Button(root, text="Close", command=lambda: close(), padx=90, pady=10)
close_button.configure(background='#374256', foreground='wheat', font=('calibri', 10, 'bold'))
close_button.pack(side=TOP, pady=30)

# Main function to build the GUI window
root.mainloop()