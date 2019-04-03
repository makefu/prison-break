import logging
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup as soup

log = logging.getLogger("hotsplots")


# TODO: put into common
def meta_redirect(content: str) -> str:
    parsed = soup(content, features="html.parser")

    result = parsed.find("meta", attrs={"http-equiv": "refresh"})
    if result:
        wait, text = result["content"].split(";")
        if text.strip().lower().startswith("url="):
            url = text[4:]
            return url
    raise Exception("Cannot find meta redirect in content")


def match_connection(connection: ConfigParser) -> bool:
    """
        return true for an open wifi spot as hotsplots only provides open spots
    """
    if "wifi" not in connection:
        log.info("Connection is not Wifi, assuming no Captive Portal")
        return False
    elif "wifi-security" in connection:
        log.info("Secured Wifi, assuming no Captive Portal")
        return False
    else:
        log.info("Unsecured wifi, might be hotsplots!")
        return True


def match(resp: requests.Response) -> bool:
    """
      resp: the initial response of the internet get request
    """
    return "www.hotsplots.de" in resp.text


def accept(resp: requests.Response, s: requests.Session) -> bool:
    """
      resp: the initial response of the internet get request
      s: the requests session for opening new http connections
    return True if successful, else False
    """

    s.headers.update({"Referer": resp.url})
    data = resp.text

    log.debug(s.headers)
    log.info("Checking for hotsplots Portal")

    # Create the POST request data from all <form> input
    parsed = soup(data, features="html.parser")
    postdata = {}

    # If this logic stops to work at some point, here are some pointers:
    #   TODO: find the correct form
    #   TODO: detect the correct URL to query based on form path and url
    for inp in parsed.find_all("input"):
        postdata[inp["name"]] = inp.get("value", "on")  # termsOK

    # First Request
    resp = s.post("https://www.hotsplots.de/auth/login.php", data=postdata)
    try:
        redirect_url = meta_redirect(resp.text)
    except Exception:
        log.warn("Got no redirect, assuming something broke")
        return False

    log.info(f"Got Redirected and follow {redirect_url}")
    s.headers.update({"Referer": resp.url})
    # Second Request
    s.get(redirect_url)
    return True
