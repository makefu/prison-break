import logging
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup as soup

log = logging.getLogger("wifionice")


def match_connection(connection: ConfigParser) -> bool:
    """
        return true for an open wifi spot as hotsplots only provides open spots
    """
    # TODO: SSID WIFIonICE
    if connection["wifi"]["ssid"].lower() == "wifionice" or \
        connection["wifi"]["ssid"].lower() == "wifi@db":
        log.info(f"SSID is {connection['wifi']['ssid']}, assuming captive portal on an DB InterCity Express")
        return True
    else:
        return False


def match(resp: requests.Response) -> bool:
    """
      resp: the initial response of the internet get request
    """
    return "www.wifionice.de" in resp.url or \
            "public-wifi.deutschebahn.com" in resp.url or \
            "wifi.bahn.de"


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

    for inp in parsed.find_all("input"):
        try:
            postdata[inp["name"]] = inp.get("value", "")  # login
        except:
            log.debug(f"Cannot update post-date from {inp}")
            pass

    # First Request
    log.info("Sending POST to login url")
    log.debug(f"data: {postdata}")

    #   TODO: detect the correct URL to query based on form path and url
    # The URL changed from http to http, and wifionice.de is now wifi.bahn.de
    resp = s.post("https://wifi.bahn.de/de/?url=http%3A%2F%2Fkrebsco.de%2Fsecret", data=postdata)
    log.debug(f"Return code: {resp.status_code}")
    log.debug(resp.headers)
    return resp.ok
