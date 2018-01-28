from imagenet_fall11_urls.URLsParser import URLsParser

class ImageDownloader:
    urls_path = ""
    dest_path = ""
    downloaded_map_path = ""

    def __init__(self, urls_path, dest_path, downloaded_map_path):
        self.urls_path = urls_path
        self.dest_path = dest_path
        self.downloaded_map_path = downloaded_map_path

    def download(self, matcher, count):
        urls_parser = URLsParser(self.urls_path, notify_interval=(10**6))
        matched = 0
        retval = []

        for group in urls_parser:
            if (matcher(group[0])):
                retval.append([urls_parser.line_num, *group])
                matched += 1
                if (matched >= count):
                    break

        return retval