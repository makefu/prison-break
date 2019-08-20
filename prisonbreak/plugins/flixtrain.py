import logging
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup as soup

log = logging.getLogger("flixbus")


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
    elif True:
        help(connection)
        log.info("Access Point Starts with Flix, may be flixbus")
    else:
        log.info("Unsecured wifi, might be flixbus!")
        return True


def match(resp: requests.Response) -> bool:
    """
      resp: the initial response of the internet get request
    """
    return "portal.moovmanage.com" in resp.text


def accept(resp: requests.Response, s: requests.Session) -> bool:
    """
      resp: the initial response of the internet get request
      s: the requests session for opening new http connections
    return True if successful, else False
    """

    s.headers.update({"Referer": resp.url})
    data = resp.text

    log.debug(s.headers)
    log.info("Checking for flixbus Portal")

    # Create the POST request data from all <form> input
    parsed = soup(data, features="html.parser")
    getdata = {}

    # If this logic stops to work at some point, here are some pointers:
    #   TODO: find the correct form
    #   TODO: detect the correct URL to query based on form path and url
    for inp in parsed.find_all("input"):
        log.debug(inp)
        if inp.get("name",None):
            log.debug(f"{inp['name']} -> {inp['value']}")
            getdata[inp["name"]] = inp.get("value")

    # First Request
    log.debug(f"Sending first request to {resp.url} with data {getdata}")
    help(s.get)
    resp = s.get(resp.url, params=getdata)

    try:
        log.debug(resp.text)
        redirect_url = meta_redirect(resp.text)
        log.debug("Got Redirect url: {redirect_url}")
    except Exception:
        log.warn("Got no redirect, assuming something broke")
        return False
    s.get(redirect_url)
    return True
