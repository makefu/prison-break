import logging
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup as soup

log = logging.getLogger("wifionice")


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
    # TODO: SSID WIFIonICE
    if connection["wifi"]["ssid"] == "WIFIonICE":
        log.info("SSID is WIFIonICE, assuming captive portal")
        return True
    else:
        return False


def match(resp: requests.Response) -> bool:
    """
      resp: the initial response of the internet get request
    """
    return "www.wifionice.de" in resp.url


def accept(resp: requests.Response, s: requests.Session) -> bool:
    """
      resp: the initial response of the internet get request
      s: the requests session for opening new http connections
    return True if successful, else False
    """

    s.headers.update({"Referer": resp.url})
    data = resp.text

    log.debug(s.headers)
    log.info("Checking for WIFIOnICE Portal")

    # Create the POST request data from all <form> input
    parsed = soup(data, features="html.parser")
    postdata = {}

    # If this logic stops to work at some point, here are some pointers:
    #   TODO: find the correct form
    #   TODO: detect the correct URL to query based on form path and url
    for inp in parsed.find_all("input"):
        postdata[inp["name"]] = inp.get("value", "")  # login

    # First Request
    log.info("Sending POST to login url")
    log.debug(f"data: {postdata}")
    resp = s.post("http://www.wifionice.de/de/?url=http%3A%2F%2Fkrebsco.de%2Fsecret", data=postdata)
    log.debug("Return code: {resp.status_code}")
    return resp.ok
