from imagenet_fall11_urls.URLsParser import URLsParser
from imagenet_fall11_urls.PrefixParser import PrefixParser
from downloadImages.ImageDownloader import ImageDownloader

def matches(prefix_parser, value):
    prefix = value.split("_")[0]
    does_match = prefix_parser.matches_prefix(prefix)
    return does_match

def get_matching_urls(urls_path, matcher, count):
    urls_parser = URLsParser(urls_path, notify_interval=(10**6))
    matched = 0
    retval = []

    for group in urls_parser:
        if (matcher(group[0])):
            retval.append(group[1])
            matched += 1
            if (matched >= count):
                break

    return retval

if __name__ == "__main__":
    urls_path = "imagenet_fall11_urls/fall11_urls.txt"
    dest_path = "downloadImages/downloads/person"
    downloaded_map_path = "downloadImages/downloads/people_map.txt"
    prefix_parser = PrefixParser("imagenet_fall11_urls/person.txt")
    prefix_parser.parse()
    matcher = lambda s: matches(prefix_parser, s)
    count = 300

    downloader = ImageDownloader(dest_path, downloaded_map_path)
    matching_urls = get_matching_urls(urls_path, matcher, count * 2)
    download_count = downloader.download(matching_urls, count)
    print(f"downloaded {download_count:,} person images")