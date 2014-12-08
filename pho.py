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
    Make pairs of soups and the names of the files they came from.
    :param dir_name: The name of the directory that has the html files needed.
    :param exclusions: Any exclusions that should NOT be considered within that directory.
    :return: A tuple containing the soup object and the name of the file used to create it.
    """
    import os

    from collections import namedtuple
    SoupFilePair = namedtuple("SoupFileName", ["soup", "file_name"])
    is_valid_file = lambda fpath: os.path.isfile(fpath) and fpath.endswith(".html") and fpath not in exclusions

    for fname in os.listdir(dir_name):
        file_path = "{0}/{1}".format(dir_name, fname)
        if is_valid_file(file_path):
            file_ob = open(file_path, "rt", encoding="utf-8")
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



