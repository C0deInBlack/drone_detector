# drone_detector

PyQt application that detects drones using a custon Haar Cascade XML training file and OpenCV.

Detect in images \
![img](https://github.com/C0deInBlack/drone_detector/blob/main/assets/img.png)

Detect in videos \
![](https://github.com/C0deInBlack/drone_detector/blob/main/assets/video.gif)

The cascade XML was created with [Cascade Trainer GUI](https://amin-ahmadi.com/cascade-trainer-gui/).

The script ![image_crawler.py](https://github.com/C0deInBlack/drone_detector/blob/main/image_crawler.py) download samples from internet using icrawler, it automatically organize the samples by category, positives and negatives.

```bash
❯ tree crawler -L 2
crawler
└── drones
    ├── classifier
    ├── n
    ├── neg.lst
    ├── p
    ├── pos.lst
    └── pos_samples.vec
```

The script ![detector.py](https://github.com/C0deInBlack/drone_detector/blob/main/detector.py) contains all the OpenCV detection logic for images and videos.

The graphical application ![main.py](https://github.com/C0deInBlack/drone_detector/blob/main/main.py) can also save the detected frames.

![img_2](https://github.com/C0deInBlack/drone_detector/blob/main/assets/img_2.png)
