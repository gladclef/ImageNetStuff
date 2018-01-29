from pathlib import Path
import threading
from collections import deque

import requests

from imagenet_fall11_urls.URLsParser import URLsParser

class ImageDownloader:
    dest_dirname = ""
    dest_path = None
    dl_urls_filename = ""
    dl_urls_file = None
    urls_collection = deque()
    threads_to_urls = {}
    max_dl_count = None
    dl_count = 0
    dl_remaining = 0
    dl_total = 0
    lock = threading.Lock()

    def __init__(self, dest_dirname, dl_urls_filename):
        self.dest_dirname = dest_dirname
        self.dl_urls_filename = dl_urls_filename

    def download(self, urls_collection, max_dl_count=None):
        # create the destination directory(s) as needed
        self.dest_path = Path(self.dest_dirname)
        dl_urls_path = Path(self.dl_urls_filename)
        self.dest_path.mkdir(parents=True, exist_ok=True)
        dl_urls_path.parent.mkdir(parents=True, exist_ok=True)
        dl_urls_path.touch()
        self.max_dl_count = max_dl_count
        self.dl_count = 0

        with dl_urls_path.open(mode='r+') as self.dl_urls_file:
            # read the current contents of the dl_urls_file
            # (to know where to resume downloading from the last point)
            dl_urls = self.__read_dl_urls_file(self.dl_urls_file)
            self.dl_total = len(dl_urls)
            print(f"found {self.dl_total} already download urls")
            self.dl_remaining = (self.max_dl_count - self.dl_total) if (self.max_dl_count != None) else None

            # retain all urls that have not yet been loaded
            self.urls_collection = deque()
            for url in urls_collection:
                if not url in dl_urls:
                    self.urls_collection.append(url)

            # start downloading!
            threads = []
            for i in range(3):
                helper = ImageDownloadHelper(self, f"T{i}", threading.current_thread())
                threads.append(helper)
                threads[-1].start()

            # wait for downloads to finish
            for t in threads:
                while t.isAlive():
                    t.join(timeout=1)

        return self.dl_count
    
    def __read_dl_urls_file(self, dl_urls_file):
        dl_urls = set()
        for line in dl_urls_file:
            line = line.strip()
            if (len(line) > 0):
                dl_urls.add(line)
        return dl_urls

    def get_next_url(self, thread):
        self.lock.acquire()

        try:
            # check if we need more downloads
            if (self.dl_remaining != None and self.dl_remaining <= 0):
                raise IndexError("no more downloads remaining")
            self.dl_remaining -= 1

            # retrieve the next url
            url = self.urls_collection.pop()
            self.threads_to_urls[thread] = url
            return url
        except IndexError as e:
            try:
                del self.threads_to_urls[thread]
            except (KeyError, IndexError):
                pass
            raise e
        finally:
            self.lock.release()

    def dl_completed(self, thread, img_data):
        # get the url
        url = self.threads_to_urls[thread]
        del self.threads_to_urls[thread]

        try:
            # save the file
            img_extension = url.split(".")[-1]
            self.lock.acquire()
            img_name = f"{self.dl_total}.{img_extension}"
            self.lock.release()
            img_path = self.dest_path.joinpath(img_name)
            with img_path.open('wb') as handler:
                handler.write(img_data)

            # note that the file has been saved
            self.lock.acquire()
            self.dl_urls_file.write(url + "\n")
            self.dl_count += 1
            self.dl_total += 1
        finally:
            self.lock.release()

        if (self.dl_count % 10 == 0):
            print(f"downloaded {self.dl_count:,} images...")

    def dl_failed(self, thread, error):
        # get the url
        url = self.threads_to_urls[thread]
        del self.threads_to_urls[thread]
        print(f"failed to download image \"{url}\": {error}")

        # update the needed count
        if (self.dl_remaining != None):
            self.dl_remaining += 1

class ImageDownloadHelper(threading.Thread):
    image_downloader = None
    parent_thread = None

    def __init__(self, image_downloader, name, parent_thread):
        self.image_downloader = image_downloader
        self.parent_thread = parent_thread
        super().__init__(name=name)

    def run(self):
        while True:
            # get the image url to download
            try:
                url = self.image_downloader.get_next_url(self)
            except IndexError as e:
                break

            # download the image
            try:
                request = requests.get(url)
                img_data = request.content
                if (request.status_code != 200):
                    raise NoDataException(f"status code {request.status_code}")
                if (len(img_data) < 10):
                    raise NoDataException("No data")
                if (len(img_data) == 2051):
                    raise NoDataException("Flickr 'this image is no longer available' image")
                if (img_data[0:9].decode("utf-8", "replace") == "<!DOCTYPE"):
                    raise NotAnImageException("not an image")
                if not self.parent_thread.is_alive():
                    return
                self.image_downloader.dl_completed(self, img_data)
            except Exception as e:
                self.image_downloader.dl_failed(self, e)

class NoDataException(Exception):
    pass

class NotAnImageException(Exception):
    pass