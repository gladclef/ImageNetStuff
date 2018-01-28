from imagenet_fall11_urls.URLsParser import URLsParser
from imagenet_fall11_urls.PrefixParser import PrefixParser
from downloadImages.ImageDownloader import ImageDownloader

def matches(prefix_parser, value):
    prefix = value.split("_")[0]
    does_match = prefix_parser.matches_prefix(prefix)
    return does_match

if __name__ == "__main__":
    urls_path = "imagenet_fall11_urls/fall11_urls.txt"
    dest_path = "downloadImages/downloads/people"
    downloaded_map_path = "downloadImages/downloads/people_map.txt"
    prefix_parser = PrefixParser("imagenet_fall11_urls/people.txt")
    prefix_parser.parse()
    matcher = lambda s: matches(prefix_parser, s)
    count = 10**6

    downloader = ImageDownloader(urls_path, dest_path, downloaded_map_path)
    matches = downloader.download(matcher, count)
    print(f"found {len(matches):,} people images")