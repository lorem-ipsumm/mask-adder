import face_recognition
from PIL import Image, ImageDraw
from time import sleep
import os
# import math


# calculate the slope given coordinates
def slope(x1, y1, x2, y2):

    # check for straight vertical line
    if (x1 == x2):
        return 0

    m = ((y2-y1)/(x2-x1))
    return m


# detect the faces in an image and export a new image file
# with boxes around the faces
def detect_faces(image):

    # load the image file
    loaded_image = face_recognition.load_image_file(image)

    # locate all faces in the image file
    face_locations = face_recognition.face_locations(loaded_image)

    # locate all landmarks in the photo
    face_landmarks = face_recognition.face_landmarks(loaded_image)

    # open the image
    im = Image.open(image)

    # get drawing context
    draw = ImageDraw.Draw(im)

    # output
    if len(face_locations) != 1:
        print(str(len(face_locations)) + " faces found")
    else:
        print("1 face found")

    # relevant features to filter for
    targets = ["bottom_lip", "top_lip", "nose_tip", "chin", "nose_bridge"]

    # intialize bounding box variables for mask
    left, top, right, bottom = (999, 0, 0, 0)

    # coordinate pairs for finding the top
    # and bottom of the nose bridge
    top_bridge = (0, 999)
    bottom_bridge = (0, 0)

    # iterate through the list of landmarks
    for landmark in face_landmarks:
        # go through each feature
        for feature in landmark.keys():
            # filter out relevant features
            if (feature in targets):
                # go through the coordinates
                for coord in landmark[feature]:
                    if (coord[1] > top and feature == "nose_bridge"):
                        # draw.line(landmark[feature], width=5, fill="red")
                        # get bridge coordinates for slope calculation
                        if (coord[1] < top_bridge[1]):
                            top_bridge = (coord[0], coord[1])
                        if (coord[1] > bottom_bridge[1]):
                            bottom_bridge = (coord[0], coord[1])

                        top = coord[1]

                    if (coord[0] < left):
                        left = coord[0]
                    # if (coord[1] < top and feature != "chin"):
                        # top = coord[1]
                    if (coord[0] > right):
                        right = coord[0]
                    if (coord[1] > bottom and feature != "chin"):
                        bottom = coord[1]

    # get bounding box size
    width = right - left
    # height = bottom - top

    rot = slope(top_bridge[1], top_bridge[0],
                bottom_bridge[1], bottom_bridge[0])

    print(top_bridge, bottom_bridge)
    print(str(rot) + "\n")

    # load the mask image
    mask = Image.open("./mask.png", "r").convert("RGBA")

    # resize to stretch across bounding box
    mask.thumbnail((width, width), Image.ANTIALIAS)

    # rotate the mask based according nose bridge slope
    rotated_mask = mask.rotate(rot * 100, expand=1)

    # set the top to right under the
    # highest point of the nose bridge
    top = top_bridge[1] + 5

    # add padding
    bottom += 30

    # paste image
    im.paste(rotated_mask, (left + 3,  top), rotated_mask)

    # visualization for mask placement
    # draw.rectangle((left, top, right, bottom), outline=(0, 255, 0), width=3)

    # clean up
    del draw

    # save new image
    im.save("output.png", "PNG")

    # wait
    sleep(2)


# iterate through faces directory
for filename in os.listdir('./faces'):
    # detect face and add mask
    detect_faces('./faces/' + filename)
