# Importing the required modules
import tkinter as tk  # Graphical User Interface toolkit to create user interactions
from tkinter import *
from tkinter import constants # Used for built-in tkinter constants
import easygui  # Used for opening the filebox window
import cv2  # OpenCV library for image transformations and image processing
import matplotlib.pyplot as plt # Used for plotting and visualizing the difference between each transformation
import os  # Used for reading/checking files and saving to directories
import sys  # Used for system functionalities

# Making the GUI main window
root = tk.Tk()

width = 400 # width for the Tk root
height = 420 # height for the Tk root

screen_width = root.winfo_screenwidth() # width of the screen
screen_height = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)

root.title('Cartoonify Your Image!') # title of the main window
root.iconbitmap(os.path.dirname(os.path.realpath(__file__)) + '\\style\\images\\rainbow.ico') # icon of the main window
root.geometry('%dx%d+%d+%d' % (width, height, x, y)) # calculate the main window and set the size of it
root.resizable(False, False) # disable resize option of the main window
background_image = PhotoImage(file = os.path.dirname(os.path.realpath(__file__)) + '\\style\\images\\gradient_blue.gif') # Tk only accepts .gif files as a background image
background_label = Label(root, image=background_image) # set the background image for the main window
background_label.place(x=0, y=0, relwidth=1, relheight=1) # arrange the position

image_path = '' # global variable image_path for different types of upload mechanisms

# fileopenbox opens the box to choose file and help us store file path as string

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
            # Keyboard interation - When pressing the SPACE, take the current camera feed and save it to the current directory 
            current_directory = os.path.dirname(os.path.realpath(__file__))
            image_path_camera_feed = current_directory + "\\photoshoot.png"
            global image_path
            image_path = image_path_camera_feed
            cv2.imwrite(image_path_camera_feed, frame)
            break
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) <1: # When user clicks the X button, quit the application
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

    # Read the image with the given path
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    print(original_image)  # The image is an array of numbers and it will be stored as a number array

    # Confirm the image selection and is it is not empty
    if original_image is None:
        print("The image cannot be found. Choose a proper image to cartoonify!")
        sys.exit()
    resize_image1 = resize_image_with_aspect_ratio(original_image, height=960)
    # plt.imshow(resize_image1, cmap='gray')

    # Convert the image into grayscale and resize the image
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    resize_image2 = resize_image_with_aspect_ratio(grayscale_image, height=960)
    # plt.imshow(resize_image2, cmap='gray')

    # Apply Median Blur technique to smoothen the image and resize the image
    smooth_grayscale_image = cv2.medianBlur(grayscale_image, 5)
    resize_image3 = resize_image_with_aspect_ratio(smooth_grayscale_image, height=960)
    # plt.imshow(resize_image3, cmap='gray')

    # Retrieve the edges for the cartoon effect by using Adaptive Threshold technique and resize the image
    get_edge = cv2.adaptiveThreshold(smooth_grayscale_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 3)
    resize_image4 = resize_image_with_aspect_ratio(get_edge, height=960)
    # plt.imshow(resize_image4, cmap='gray')

    # Apply bilateral filter to remove noisy data and keep the edges sharp as required and resize the image 
    color_image = cv2.bilateralFilter(original_image, 9, 300, 300)
    resize_image5 = resize_image_with_aspect_ratio(color_image, height=960)
    # plt.imshow(resize_image5, cmap='gray')

    # Mask the edged image with Bitwise AND technique to beautify the image
    cartoon_image = cv2.bitwise_and(color_image, color_image, mask=get_edge)
    global resize_image6 # must be declared to be reachable outside of the scope
    resize_image6 = resize_image_with_aspect_ratio(cartoon_image, height=960)
    # plt.imshow(resize_image6, cmap='gray')

    # Plotting all the image transformations to see the difference between each tranformation
    images = [resize_image1, resize_image2, resize_image3, resize_image4, resize_image5, resize_image6]
    fig, axes = plt.subplots(3, 2, figsize=(8, 8), subplot_kw={'xticks': [], 'yticks': []},
                             gridspec_kw=dict(hspace=0.1, wspace=0.1))
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i], cmap='gray')

    if resize_image6 is None:
        save_button.config(state=DISABLED)
    else:
        save_button.config(state=NORMAL)

    # Show all the image transformations
    plt.show()

# Resize the image with keeping the aspect ratio
def resize_image_with_aspect_ratio(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the dimensions
        r = height / float (h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def save(resize_image6, image_path):
    # Save the image with imwrite function to the working directory
    new_name = "cartoonified_" + os.path.basename(image_path)
    original_filepath = os.path.dirname(image_path)
    print(original_filepath)
    path = os.path.join(original_filepath, new_name)
    cv2.imwrite(path, cv2.cvtColor(resize_image6, cv2.COLOR_RGB2BGR))
    I = "Image saved by name " + new_name + " at " + path
    tk.messagebox.showinfo(title="Save Info", message=I)

def close():
    root.destroy() # When user presses the Close button, kill the application

# Making the Cartoonify an Image button in the GUI main window
upload = Button(root, text="Cartoonify an Image", command=upload, padx=50, pady=10)
upload.configure(background="#374256", foreground="wheat", font=('calibri', 10, 'bold'))
upload.pack(side=TOP, pady=30)

# Making the Cartoonify Image from Camera button in the GUI main window
upload_from_camera = Button(root, text="Cartoonify Image from Camera", command=upload_from_camera, padx=20, pady=10)
upload_from_camera.configure(background="#374256", foreground="wheat", font=('calibri', 10, 'bold'))
upload_from_camera.pack(side=TOP, pady=30)

# Making the Save Cartoonified Image button in the GUI main window
save_button = Button(root, text="Save Cartoonified Image", state=DISABLED, command=lambda: save(resize_image6, image_path), padx=38, pady=10)
save_button.configure(background='#374256', foreground='wheat', font=('calibri', 10, 'bold'))
save_button.pack(side=TOP, pady=30)

# Making Close button in the GUI main window
close_button = Button(root, text="Close", command=lambda: close(), padx=90, pady=10)
close_button.configure(background='#374256', foreground='wheat', font=('calibri', 10, 'bold'))
close_button.pack(side=TOP, pady=30)

# Main function to build the GUI window
root.mainloop()