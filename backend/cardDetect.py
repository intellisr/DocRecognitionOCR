import cv2
import numpy as np
from pathlib import Path

path=str(Path.cwd())+"/images/sra.jpeg"

im = cv2.imread(path, 1)

#--- convert the image to HSV color space ---
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
cv2.imshow('H', hsv[:,:,0])
cv2.imshow('S', hsv[:,:,1])

#--- find Otsu threshold on hue and saturation channel ---
ret, thresh_H = cv2.threshold(hsv[:,:,0], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
ret, thresh_S = cv2.threshold(hsv[:,:,1], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

#--- add the result of the above two ---
cv2.imshow('thresh', thresh_H + thresh_S)

#--- some morphology operation to clear unwanted spots ---
kernel = np.ones((5, 5), np.uint8)
dilation = cv2.dilate(thresh_H + thresh_S, kernel, iterations = 1)
cv2.imshow('dilation', dilation)
#--- find contours on the result above ---
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

#--- since there were few small contours found, retain those above a certain area ---
im2 = im.copy()
count = 0
for c in contours:
    if cv2.contourArea(c) < 400:
        count+=1
        cv2.drawContours(im2, [c], -1, (0, 255, 0), 2)

cv2.imshow('cards_output', im2)
cv2.waitKey()
print('There are {} cards'.format(count))