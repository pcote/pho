"""
pho.py
A collection of little useful screen scraping utilities.
"""
from functools import wraps
from time import sleep, time
from random import Random, seed
import requests
from bs4 import BeautifulSoup


def randomsleep(func):
    """
    Intentionally delays return of a function for a random number of seconds.
    :param func:
    :return:
    """

    @wraps(func)
    def wrapped_func(*args):
        result = func(*args)
        random = Random()
        random.seed(time())
        MINTIME, MAXTIME = 3, 8
        sleep_time = random.randrange(MINTIME, MAXTIME)
        print("CALLED {0} WITH ARGS {1} SLEEPING {2} seconds".format(func.__name__, str(args), sleep_time))
        sleep(sleep_time)
        return result
    return wrapped_func


def download_html_files(list_of_links, target_folder):
    """
    Downloads the files associated with a list of links to
    a local folder.
    note: There is an intentional random delay between downloads so as not to do rapid fire hammering of the
    target server.
    :param list_of_links: URL addresses to the intended files.
    :param target_folder: The path to the local folder to save files to
    :return: Nothing.
    """
    import re

    def _setup_file_path(lnk):

        new_file_name = lnk.split("/")[-1]
        file_extension_match = r"\.\w+"
        if re.search(file_extension_match, lnk ):
            new_file_name = re.sub(file_extension_match, "", new_file_name)

        new_file_name += ".html"

        return "{0}/{1}".format(target_folder, new_file_name)


    @randomsleep
    def _download(lnk, target_path):
        import requests
        import os

        res = requests.get(lnk)
        raw_data = res.text
        file_mode = "wt" if os.path.exists(target_folder) else "xt"
        with open(target_path, file_mode, encoding="utf-8") as file_ob:
            file_ob.write(raw_data)


    for link in list_of_links:
        targ_path = _setup_file_path(link)
        _download(link, targ_path)


def make_soup(fname):
    """
    Create a simple beautiful soup object out of the filename
    """
    if fname.startswith("http"):
        return BeautifulSoup(requests.get(fname).text.encode("utf-8"))
    with open(fname, "rt", encoding="utf-8") as file_ob:
        soup = BeautifulSoup(file_ob)
        return soup


def soup_line(dir_name, *exclusions):
    """
     Pair up soups with the files they're based on.
    :param dir_name: Directory with the html files needed.
    :param exclusions: Don't include these files.
    :return: A tuple of soup file name pairs.
    """
    import os

    from collections import namedtuple
    SoupFilePair = namedtuple("SoupFileName", ["soup", "file_name"])

    def is_valid_file(fpath):
        if os.path.isfile(fpath):
            if fpath.endswith(".html"):
                if fpath not in exclusions:
                    return True
        else:
            return False


    for fname in os.listdir(dir_name):
        file_path = "{0}/{1}".format(dir_name, fname)
        if is_valid_file(file_path):
            with open(file_path, "rt", encoding="utf-8") as file_ob:
                soup = BeautifulSoup(file_ob.read().strip())
                yield SoupFilePair(soup, fname)


if __name__ == '__main__':
    ###########################
    # TEST RUN CODE           #
    ##########################
    """
    download_html_files downloads a list of files based on urls specified in a list.
    It's set up with a random sleeper timer so not to alarm server admins and getting your ip address blocked.
    """
    target_urls =  ["http://www.reddit.com/r/python", "https://news.ycombinator.com"]
    download_html_files(target_urls, "sources")

    """
    soup_line is a generator function that makes Beautiful soup objects out of files in the directory specified.
    Each turn of the generator brings a new soup object along with the name of the file used to create it.
    The user can include files to NOT include.  For example, maybe you want category web pages but NOT the original
    category page they're all associated with.
    """
    for soup, file_name in soup_line("sources"):
        print(file_name, soup("title"))

    """
    The make_soup utility is a convenience function that can work with either a local file or a url.
    """
    second_soup = make_soup("sources/python.html")
    print(second_soup("title"))
    third_soup = make_soup("http://httpbin.org")
    print(third_soup("title"))



