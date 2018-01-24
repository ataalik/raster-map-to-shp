#!/usr/bin/python

#
# Implements 8-connectivity connected component labeling
#
# Algorithm obtained from "Optimizing Two-Pass Connected-Component Labeling
# by Kesheng Wu, Ekow Otoo, and Kenji Suzuki
#

from PIL import Image, ImageDraw, ImageFilter
from collections import defaultdict
import sys, os
import math, random
from itertools import product
from ufarray import *
import os
from random import choice
from string import ascii_uppercase

def run(img):
    data = img.load()
    width, height = img.size

    # Union find data structure
    uf = UFarray()

    #
    # First pass
    #

    # Dictionary of point:label pairs
    labels = {}

    for y, x in product(range(height), range(width)):

        #
        # Pixel names were chosen as shown:
        #
        #   -------------
        #   |   | b |   |
        #   -------------
        #   | a | c |   |
        #   -------------
        #   |   |   |   |
        #   -------------
        #
        # The current pixel is c
        # a, and b are its neighbors of interest
        #
        # 255 is white, 0 is black
        # White pixels part of the background, so they are ignored
        # If a pixel lies outside the bounds of the image, it default to white
        #

        # If the current pixel is white, it's obviously not a component...
        if data[x, y] == 255:
            pass

        # If pixel b is in the image and black:
        #    so simply assign b's label to c
        elif y > 0 and data[x, y-1] == 0:
            b = labels[(x, y-1)]
            labels[x, y] = b
            # If pixel a is in the image and black:
            #    Then b and a are connected through c
            #    Therefore, we must union their sets
            if x > 0 and data[x-1, y] == 0:
                a = labels[(x-1, y)]
                uf.union(b, a)

        # If pixel a is in the image and black
        #    We already know b is white
        #    so simpy assign a's label to c
        elif x > 0 and data[x-1, y] == 0:

            labels[x, y] = labels[(x-1, y)]


        # All the neighboring pixels are white,
        # Therefore the current pixel is a new component
        else:
            labels[x, y] = uf.makeLabel()

    #
    # Second pass
    #

    uf.flatten()

    colors = {}
    components = defaultdict(list)

    # Image to display the components in a nice, colorful way
    output_img = Image.new("RGB", (width, height))
    outdata = output_img.load()

    for (x, y) in labels:

        # Name of the component the current point belongs to
        component = uf.find(labels[(x, y)])

        # Update the labels with correct information
        labels[(x, y)] = component
        components[labels[(x, y)]].append((x,y))

        # Associate a random color with this component
        if component not in colors:
            colors[component] = (random.randint(0,255), random.randint(0,255),random.randint(0,255))

        # Colorize the image
        outdata[x, y] = colors[component]

    return (labels, output_img, components)


def main():



    #SIDEBAR LOCATION TO CROPOUT
    map_area_end = 1042

    # Open the image
    img = Image.open(sys.argv[1])
    pix = img.load()


    #year we are processing
    year = os.path.splitext(os.path.basename(sys.argv[1]))[0]

    if not os.path.exists('output/' + year):
        os.mkdir('output/' + year)
    else:
        os.system('rm -rf output/' + year + "/*")
    width, height = img.size


    #WORKAROUNDS to be changed for each new map set
    #img = img.crop((0,0,map_area_end,height))

    width, height = img.size
    img = img.convert('RGBA')


    datas = img.getdata()

    newData = []
    ther = 60
    upperTher = 230

    #Erase the borders and text from image
    for item in datas:
        if item[0] < ther and item[1] < ther and item[2] < ther:
            newData.append((255, 255, 255,0))
        elif item[0] > upperTher and item[1] > upperTher and item[2] > upperTher:
            newData.append((255, 255, 255,0))
        else:
            newData.append((0, 0, 0, 255))

    img.putdata(newData)
    img = img.convert("RGB")

    # Threshold the image, this implementation is designed to process b+w
    # images only
    img = img.point(lambda x: 0 if x<190 else 255)
    img = img.convert('1')


    #Dilate and erode to make sure gaps in the borders are filled
    img = img.filter(ImageFilter.MaxFilter(3))
    img = img.filter(ImageFilter.MinFilter(3))


    # labels is a dictionary of the connected component data in the form:
    #     (x_coordinate, y_coordinate) : component_id
    #
    # if you plan on processing the component data, this is probably what you
    # will want to use
    #
    # output_image is just a frivolous way to visualize the components.
    (labels, output_img, components) = run(img)

    for component in components:
        #The component is too small so probably an artifact.
        if len(components[component]) > 30:
            label_img = Image.new("RGBA", (width, height))

            outdata = label_img.load()

            #Paint the component red
            for (x,y) in components[component]:
                outdata[x,y] = (255,0,0)


            #Paint the transparent pixels outside the component green
            for i in range(0,width):
                if(label_img.getpixel((i,0)) == (0,0,0,0)):
                    ImageDraw.floodfill(label_img, (i,0),(0,255,0,255))

                if(label_img.getpixel((i,height-1)) == (0,0,0,0)):
                    ImageDraw.floodfill(label_img, (i,height-1),(0,255,0,255))

            for i in range(0,height):
                if(label_img.getpixel((0,i)) == (0,0,0,0)):
                    ImageDraw.floodfill(label_img, (0,i),(0,255,0,255))
                if(label_img.getpixel((width-1,i)) == (0,0,0,0)):
                    ImageDraw.floodfill(label_img, (width-1,i),(0,255,0,255))

            oldData = label_img.getdata()
            newData = []

            # If a pixel is green than it's outside so it should be transparent
            # Everything else should be painted before the conversion.
            # This is done in order to make sure the component is completely filled.
            for item in oldData:
                if item == (0,255,0,255):
                    newData.append((255, 255, 255,0))
                else:
                    newData.append((255, 0, 0, 255))

            label_img.putdata(newData)



            random_name = ''.join(choice(ascii_uppercase) for i in range(12))
            img_path = "output/" + year + "/" + random_name

            # Edit your gdal translate, gdalwarp and gdal_edit commands according to your needs (like adding georeference points or an SRS) then uncomment
            # translate_string = "gdal_translate -q -of GTiff " + img_path + ".png /tmp/rasterconversiontemp"
            # warp_string = "gdalwarp -q -r cubicspline -tps -co COMPRESS=NONE  /tmp/rasterconversiontemp " + img_path + ".tiff"
            # update_string = "gdal_edit.py " + img_path + ".tiff"
            #label_img.save(img_path + ".png", "PNG")
            #os.system(translate_string)
            #os.system(warp_string)
            #os.system(update_string)
            #os.system("gdal_polygonize.py " +  img_path + ".tiff" + " -f  ESRI\ Shapefile " + "output/" + year + "/" + random_name + ".shp")
            #os.system("rm output/" + year + "/" + random_name + ".tiff")
            #os.system("rm output/" + year + "/" + random_name + ".png")

if __name__ == "__main__": main()
