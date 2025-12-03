#!/usr/bin/python3

import sys; sys.path.append("./LIBS/lib/python3.13/site-packages/")
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import numpy
import os
from detector import Detector
from typing import Optional
import cv2 as cv

class Globals:
    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.run_image: bool = False

globals_ = Globals(0,0) 

class MainUI(QMainWindow,):
    resized = pyqtSignal()
    def __init__(self, *args, **kargs) -> None:
        super().__init__(*args, **kargs)

        uic.loadUi("app.ui", self)

        self.image_button.clicked.connect(self.browse_image)
        self.cascade_button.clicked.connect(self.browse_cascade)
        self.run_button.clicked.connect(self.run)
        self.video_button.clicked.connect(self.browse_video)

        self.cancel_button.clicked.connect(self.cancel_process)

        self.scale_factor.valueChanged.connect(self.update_values)
        self.minimum_neighbors.valueChanged.connect(self.update_values)
        
        self.scale_factor.sliderReleased.connect(self.run)
        self.minimum_neighbors.sliderReleased.connect(self.run)

        self.image_file: str = ""
        self.cascade_file: str = ""
        self.video_file: str = ""
        self.save_img: bool = False

        self.sF_value.setText(str(self.scale_factor.value()/10))
        self.mN_value.setText(str(self.minimum_neighbors.value()))

        self.thread = QThread()
        self.thread.setTerminationEnabled()

        self.resized.connect(self.set_layout_size) # On resize event, execute the function

        self.capture_checkbox_2.stateChanged.connect(self.save_detected)

    def browse_image(self) -> None:
        self.video_file = ""
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select an image", os.getcwd(), "Images (*.png *.jpg)", options=options
        )
        if filename:
            self.image_file = filename
            self.image_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
            self.video_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
        else: self.image_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """) 
        if self.image_file and self.cascade_file: self.run()

    def browse_video(self) -> None:
        self.image_file = ""
        options = QFileDialog.Options()
        video, _ = QFileDialog.getOpenFileName(
            self, "Select an video", os.getcwd(), "Video (*.mp4 *.webm)", options=options
        )
        if video:
            self.video_file = video
            self.video_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
            self.image_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
        else: self.video_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """) 
    def browse_cascade(self) -> None:
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select a XML", os.getcwd(), "Cascade file (*.xml)", options=options
        )
        if filename:
            self.cascade_file = filename
            self.cascade_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
        else: self.cascade_button.setStyleSheet("""
                QPushButton {
                    border-color: rgb(85, 85, 127);
                    border-width:1px;
                    border-style: inset;
                }
                QPushButton::pressed { 
                    border-color: rgb(156, 156, 156);
                }
            """)
        if self.image_file and self.cascade_file: self.run()

    def message_box(self, text: str) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()

    def run(self) -> None:
        if not self.cascade_file: return
       
        self.worker = Worker(self.cascade_file,
                             float(self.scale_factor.value()/10),
                             int(self.minimum_neighbors.value()),
                             self.image_file, self.video_file)

        self.worker.moveToThread(self.thread)

        if self.image_file and not self.video_file: self.thread.started.connect(self.worker.detect_image)
        if self.video_file and not self.image_file and self.cascade_file: self.thread.started.connect(self.worker.detect_video)

        self.worker.img_frame.connect(self.update_frame)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()
         
    def update_frame(self, img: Optional[QImage]) -> None:
        pixmap = QPixmap.fromImage(img)
        self.image_label.setPixmap(pixmap)

    def update_values(self) -> None:
        self.sF_value.setText(str(self.scale_factor.value()/10))
        self.mN_value.setText(str(self.minimum_neighbors.value()))

    def cancel_process(self) -> None:
        globals_.run_image = False
        self.image_label.clear() # Clear the PIXmap image
        self.image_label.adjustSize() # Auto adjust the label size
        self.thread.terminate()

    def get_label_size(self) -> tuple[int, int]:
        #print(int(self.image_label.size().width()), int(self.image_label.height()))
        return int(self.image_label.size().width())-10, int(self.image_label.height())-10

    def resizeEvent(self, event):
        self.resized.emit()
        #self.image_label.setGeometry(0, 0, 0, 0)
        return super(MainUI, self).resizeEvent(event)

    def set_layout_size(self):
        globals_.width, globals_.height = self.get_label_size()

    def save_detected(self, value) -> None:
        state = Qt.CheckState(value)
        if state == Qt.CheckState.Checked: self.save_img = True 
        elif state == Qt.CheckState.Unchecked: self.save_img = False

class Worker(QThread):
    finished = pyqtSignal()
    img_frame = pyqtSignal(QImage)

    def __init__(self, cascade: str, sF: float, mN: int, img: str, video: str) -> None:
        super().__init__()
        self.cascade: str = cascade 
        self.sF: float = sF 
        self.mN: int = mN 
        self.img: str = img 
        self.video: str = video

    def detect_image(self) -> None: 
        img_ = Detector(self.cascade, self.sF, self.mN, self.img, self.video)
        frame = img_.read_img()

        globals_.run_image = True

        while(globals_.run_image):
            try: frame = cv.resize(frame, (globals_.width, globals_.height))
            except Exception: pass

            img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            self.img_frame.emit(img) 
            self.finished.emit()

    def detect_video(self) -> None:
        img_ = Detector(self.cascade, self.sF, self.mN, self.img, self.video)
        for frame, ret in img_.read_video(detect_=ui.save_img):
            if ret:
                try: frame = cv.resize(frame, (globals_.width, globals_.height))
                except Exception: ui.message_box("failed resizing")

                img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
                self.img_frame.emit(img) 

        self.finished.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec_()
