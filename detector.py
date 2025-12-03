#!/usr/bin/python3

import sys, os, argparse
sys.path.append("./LIBS/lib/python3.13/site-packages/")
import cv2 as cv 
from matplotlib import pyplot as plt 
from termcolor import colored 
import numpy
from typing import Optional, Generator

class Detector:
    def __init__(self, cascade: str, scale_factor: float, minimum_neighbors: int, img: str = "", video: str = "", main_script:bool=False) -> None:
        self.cascade: list[str] = cascade
        self.img: str = img
        self.video: str = video
        self.scale_factor: float = scale_factor
        self.minimum_neighbors: int = minimum_neighbors
        self.main_script: bool = main_script

    def draw(self, detected: numpy.ndarray, img: numpy.ndarray, color: tuple[int], message: str, counter:int, img_msg:str="", detect:bool=False) -> None:
        overlay = img.copy()
        alpha: float = 0.6
        for (x, y, w, h) in detected:
            cv.rectangle(overlay, (x,y), (x + w, y + h), color, 2)
            cv.rectangle(overlay, (x,y), (x + w, y-20), color, -1) # text background
            cv.putText(overlay, message, (x,y-5), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
               
            if detect:
                cv.addWeighted(overlay, alpha, img, 1-alpha, 0, img)
                img_ = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                os.makedirs(os.path.join("assets", "detected"), exist_ok=True)
                cv.imwrite(os.path.join("assets/detected", f"detected_{img_msg}_{counter}.png"), img_) 

        cv.addWeighted(overlay, alpha, img, 1-alpha, 0, img)
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)   

    def read_video(self, width:int=800, height:int=400, detect_:bool=False) -> Generator[tuple[Optional[numpy.ndarray], bool], None, None]: # YieldType, SendType, ReturnType
        try:
            with open(self.video, 'rb') as f: pass
        except FileNotFoundError: print(colored(f"[!] Video {self.video} not found", "yellow")); sys.exit(1)

        #for i in self.cascade:
        #try:
            #with open(i, 'rb') as f: pass 
        #except FileNotFoundError: print(colored(f"[!] Training file {i} not found", "yellow")); sys.exit(1)
        
        cap = cv.VideoCapture(self.video)
        cap.set(3, 640)
        cap.set(4, 420)

        cascade_drones = cv.CascadeClassifier(self.cascade)
        #cascade_drones = cv.CascadeClassifier(self.cascade[0])
        #cascade_guns = cv.CascadeClassifier(self.cascade[1])

        counter: int = 0
        while (cap.isOpened()):
            ret, frame = cap.read()
            if not ret: 
                if __name__ == "__main__": break
                else: yield frame, ret; break

            img = cv.resize(frame, (width, height))
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

            detect_drones, rejectLevels, levelWeights_drones = cascade_drones.detectMultiScale3(img_gray, self.scale_factor, self.minimum_neighbors, outputRejectLevels=True)
            #detect_guns, _, levelWeights_guns = cascade_guns.detectMultiScale3(img_gray, self.scale_factor, self.minimum_neighbors, outputRejectLevels=True)

            try: self.draw(detect_drones, img, (255, 0, 0), f"drone {levelWeights_drones[0]:.2f}", counter, detect=detect_) 
            except IndexError: pass 
        
            #try: self.draw(detect_guns, img, (255, 85, 0), f"gun {levelWeights_guns[0]:.2f}", counter) 
            #except IndexError: pass

            if self.main_script: img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

            counter += 1

            if self.main_script:
                cv.imshow('Frame', img)
                if cv.waitKey(10) & 0xFF == ord('q'): break
            else: yield img, ret 

        cap.release()
        if self.main_script: cv.destroyAllWindows()

    def read_img(self, width: int = 800, height: int = 400) -> Optional[numpy.ndarray]:
        try:
            with open(self.img, 'rb') as f: pass
        except FileNotFoundError: print(colored(f"[!] Image {self.img} not found", "yellow")); sys.exit(1)

        #for i in self.cascade:
        #try:
            #with open(i, 'rb') as f: pass 
        #except FileNotFoundError: print(colored(f"[!] Training file {i} not found", "yellow")); sys.exit(1)

        img = cv.imread(self.img)
        img = cv.resize(img,(width, height))
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) 
       
        cascade_drones = cv.CascadeClassifier(self.cascade)
        # cascade_drones = cv.CascadeClassifier(self.cascade[0])
        # cascade_guns = cv.CascadeClassifier(self.cascade[1])

        # Detect, rejectLevels, levelWeights
        detect_drones, rejectLevels, levelWeights_drones = cascade_drones.detectMultiScale3(img_gray, self.scale_factor, self.minimum_neighbors, outputRejectLevels=True)
        #detect_guns, _, levelWeights_guns = cascade_guns.detectMultiScale3(img_gray, self.scale_factor, self.minimum_neighbors, outputRejectLevels=True)

        try: self.draw(detect_drones, img, (255, 0, 0), f"drone {levelWeights_drones[0]:.2f}", 0) 
        except IndexError: pass 
    
        #try: self.draw(detect_guns, img, (255, 85, 0), f"gun {levelWeights_guns[0]:.2f}", 0) 
        #except IndexError: pass

        if self.main_script: img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        if self.main_script:
            while (True):
                cv.imshow('Frame', img)
                if cv.waitKey(10) & 0xFF == ord('q'): break
            
            cv.destroyAllWindows()
        else: return img 
 
def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cascade", type=str, default="", help="Cascade files")
    parser.add_argument("-i", "--image", type=str, default="", help="Image to test")
    parser.add_argument("-v", "--video", type=str, default="", help="Video to test")
    args = parser.parse_args()

    return parser, args

if __name__ == "__main__":
    parser, args = args()
    
    if not args.cascade: parser.print_help(); sys.exit(1)

    #args.cascade = args.cascade.split(',')

    detector = Detector(args.cascade, 6.0, 17, args.image, args.video, True)
    
    if args.image and not args.video: detector.read_img(800, 400)
    if args.video and not args.image: 
        next(detector.read_video(800, 400))
