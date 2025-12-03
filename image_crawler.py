#!/usr/bin/python3 

import sys; sys.path.append("./LIBS/lib/python3.13/site-packages/")
import os, shutil
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler, BaiduImageCrawler
import cv2 as cv

class ImageCrawler:
    def __init__(self,keyword: str, categories: list[str], quantity: int, negatives:list[str]=["trees", "desert", "human faces"]) -> None:
        self.keyword: str = keyword
        self.categories: list[str] = categories
        self.quantity: int = quantity
        self.negatives: list[str] = negatives 

    def spidering(self) -> None:
        for i in self.categories:
            try: os.makedirs(os.path.join(f"crawler_tmp/{i}", "p"), exist_ok=True)
            except Exception as e: print(e)
           
            crawler = GoogleImageCrawler(storage={"root_dir":f"crawler_tmp/{i}/p"})
            crawler.crawl(keyword=i, filters=None, max_num=self.quantity, offset=0)
        
    def negative_spidering(self) -> None:
        for i, j in zip(self.negatives, self.categories): 
            try: os.makedirs(os.path.join(f"crawler_tmp/{j}", "n"))
            except Exception as e: print(e)

            crawler = GoogleImageCrawler(storage={"root_dir":f"crawler_tmp/{j}/n"})
            crawler.crawl(keyword=i, filters=None, max_num=self.quantity, offset=0)

    def organize(self) -> None:
        os.makedirs(os.path.join("crawler_tmp", "organized"), exist_ok=True)
        os.makedirs(os.path.join("crawler_tmp/organized", "p"), exist_ok=True)
        os.makedirs(os.path.join("crawler_tmp/organized", "n"), exist_ok=True)
        
        counter: int = 0
        for directory in os.listdir("crawler_tmp"):
            try:
                if directory == "organized": break
                positives: str = os.path.join(f"crawler_tmp/{directory}", "p")

                for img in os.listdir(os.path.join(positives)):
                    name: str = os.path.join(positives, img)
                    new_name = os.path.join("crawler_tmp/organized/p", f"{counter:06d}.{img.split('.')[1]}")

                    shutil.copy(os.path.join(name), os.path.join(new_name))
                    
                    #resized_img = cv.resize(cv.imread(os.path.join(new_name)), (800, 400))
                    #cv.imwrite(os.path.join(new_name), resized_img)
                    
                    counter += 1
            except Exception as e: print(e); break
        counter=0

        for directory in os.listdir("crawler_tmp"):
            try:
                if directory == "organized": break
                negatives: str = os.path.join(f"crawler_tmp/{directory}", "n")

                for img in os.listdir(os.path.join(negatives)):
                    name: str = os.path.join(negatives, img)
                    new_name = os.path.join("crawler_tmp/organized/n", f"{counter:06d}.{img.split('.')[1]}")
                    
                    shutil.copy(os.path.join(name), os.path.join(new_name))
                    
                    #resized_img = cv.resize(cv.imread(os.path.join(new_name)), (800, 400))
                    #cv.imwrite(os.path.join(new_name), resized_img)

                    counter += 1

                shutil.rmtree(os.path.join("crawler_tmp", directory))
            except Exception as e:
                print(e);
                shutil.rmtree(os.path.join("crawler_tmp", directory))
                break
        counter=0

        #os.rename(os.path.join("crawler_tmp", "organized"), os.path.join("crawler_tmp", self.keyword))
        shutil.copytree(os.path.join("crawler_tmp" ,"organized"), os.path.join("crawler", self.keyword))
        shutil.rmtree(os.path.join("crawler_tmp"))

if __name__ == "__main__":
    image_crawler = ImageCrawler("drones", ["drones"], 100)
    image_crawler.spidering()
    image_crawler.negative_spidering()
    image_crawler.organize()
