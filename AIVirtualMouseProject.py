import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

#########################
wCam, hCam = 640, 480
frameR = 100   # Frame reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0    # previous location of X and Y
clocX, clocY = 0, 0

cap = cv2.VideoCapture(1)
cap.set(3, wCam)  # width
cap.set(4, hCam)   # height
detector = htm.handDetector(maxHands=1)
wScr, hScr =autopy.screen.size()   # get exact size of the screen
#print(wScr, hScr)

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. Get the tip of the index and middle fingers
    if len(lmList)!= 0:
        x1, y1 = lmList[8][1:]      # coordinates of index finger
        x2, y2 = lmList[12][1:]     # coordinates of middle finger
        #print(x1, y1, x2, y2)

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        #print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)  # range for cursor

        # 4. Only Index Finger : Moving Mode
        if fingers[1]==1 and fingers[2]==0:

            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))  # width of screen
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))  # height of screen

            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening  # current location of X and Y
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            autopy.mouse.move(wScr-clocX, clocY)
            cv2.circle(img, (x1, y1),
                       15, (255, 0, 255), cv2.FILLED ) # img,  , radius=15, color=purple, filled
            plocX, plocY = clocX, clocY

        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:

            # 9. Find distance between fingers
            length, img, lineInfo= detector.findDistance(8, 12, img)  # landmark coordinates
            print(length)

            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 255, 0), cv2.FILLED)  # img,  , radius=15, color=green , filled
                autopy.mouse.click()

    # 11. Frame Rate
    cTime =time.time()
    fps = 1/(cTime-pTime)  # current time - previous time
    pTime = cTime
    cv2.putText(img,str(int(fps)),(20,50),cv2.FONT_HERSHEY_PLAIN, 3,     # position (20,50), Font style, Font scale, Font color ,thickness
                (255, 0, 0),3)

    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)
