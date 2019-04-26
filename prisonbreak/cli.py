"""usage: prison-break [options] [INTERFACE STATUS]

options:
    --debug             enable super duper debugging
    --force-run         unconditional run even if no CONNECTION_FILENAME is set
    --force-token       continue even if we received the correct token
    --force-match       continue for each plugin even if match returned False
    --timeout=SEC       Receive Timeout in seconds before failing [Default: 10]

the active prison-break connection profile may be set via
CONNECTION_FILENAME environment variable. This is used to check if the
connection might be a captive portal via all available plugins
"""
import configparser
from docopt import docopt
from os import environ
from sys import exit
import logging
log = logging.getLogger('cli')
import requests
from straight.plugin import load


def configure_debug(debug: bool) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        from http.client import HTTPConnection

        HTTPConnection.debuglevel = 1
        log.setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        log.debug("HTTP debugging enabled")
    else:
        logging.basicConfig(level=logging.INFO)
        log.setLevel(logging.INFO)


def main():
    args = docopt(__doc__)
    configure_debug(args["--debug"])
    secret_url = "http://krebsco.de/secret"  # return 1337
    profile = environ.get("CONNECTION_FILENAME", None)
    timeout = float(args['--timeout'])
    # plugins implement:
    #  match_connection: check connection profile is a possible hotspot (optional)
    #  match: check if the initial request is possibly the hotspot of the  plugin
    # accept: click the "accept AGB" button of the hotspot
    plugins = load("prisonbreak.plugins")

    if args['--force-run']:
        log.info("CONNECTION_FILENAME environment is not set"
                  "and --force-run is set, assuming unconditional run")
    elif args['STATUS'] == 'down':
        log.info('device went down, doing nothing')
        exit(0)
    elif not profile:
        log.info("CONNECTION_FILENAME environment is not set"
                  ", assuming run as condition-change and doning nothing")
        exit(0)
    else:
        log.info("CONNECTION_FILENAME set"
                 ", checking if any plugin matches connection pattern")
        matched = False
        config = configparser.ConfigParser()
        config.read(profile)
        for plug in plugins:
            if "match_connection" in dir(plug):
                log.debug(f"running match() provided by {plug}")
                if plug.match_connection(config):
                    matched = True
            else:
                log.debug(f"{plug} does not provide matching function")
        if matched:
            log.info("at least one plugin matched Connection"
                     " for being a possible AGB prison")
        else:
            log.info("no plugin matched connection profile"
                     ", exiting")
            exit(0)

    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:65.0)"
                          "Gecko/20100101 Firefox/65.0"
        }
    )
    initial_response = s.get(secret_url,timeout=timeout)

    if initial_response.text.startswith("1337"):
        log.info("Received the correct challenge token"
                 ", assuming no captive portal")
        if args['--force-token']:
            log.info("Continuing even though we got the correct token!")
        else:
            exit(0)

    for plug in plugins:
        name = plug.__name__
        log.info(f"Running Plugin {name}")
        matched = plug.match(initial_response)
        if args['--force-match']:
            log.info("Force-match set, skipping plugin match."
                     f"Response would be {matched}")
        elif not matched:
            log.info(f"{name} cannot log into hotspot")
            continue
        if plug.accept(initial_response, s):
            log.info(f"{name} successful?")
            if s.get(secret_url,timeout=timeout).text.startswith("1337"):
                log.info(f"{name} successful!")
                exit(0)
            else:
                log.warn(f"{name} failed to break free, continuing")

        else:
            log.info(f"{name} returned False, continuing")

    log.error("No plug was able to establish a connection")


if __name__ == "__main__":
    main()
