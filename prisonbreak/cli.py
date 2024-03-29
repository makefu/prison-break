"""usage: prison-break [options] [INTERFACE STATUS]

options:
    --debug             enable super duper debugging
    --force-run         unconditional run even if no CONNECTION_FILENAME is set
    --force-token       continue even if we received the correct token
    --force-match       continue for each plugin even if match returned False
    --timeout=SEC       Receive Timeout in seconds before failing [Default: 5]
    --timeout-wait=SEC  Seconds to wait after a failed timeout [Default: 1]
    --wait=SEC          Seconds to wait before trying to log in [Default: 3]
    --retry=NUM         Retry the initial connection on timeout [Default: 3]
    --no-notify            disable notifications

the active prison-break connection profile may be set via
CONNECTION_FILENAME environment variable. This is used to check if the
connection might be a captive portal via all available plugins
"""
import configparser
from docopt import docopt
from os import environ
from sys import exit
from time import sleep
import logging
log = logging.getLogger('cli')
import notify2
import os
import functools
import requests
from requests import Timeout
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

def send_notify(message,title="Prison-Break",icon="dialog-warning-symbolic",do_notify=True,timeout=10,critical=False):
    if do_notify:
        log.debug(f"Notify summary={title}, message={message}")
        n = notify2.Notification(summary=title,icon=icon,message=message)
        if critical:
            n.set_urgency(notify2.URGENCY_CRITICAL)
        n.set_timeout(timeout*1000)
        n.show()


def main():
    args = docopt(__doc__)
    secret_url = "http://krebsco.de/secret"  # return 1337
    profile = environ.get("CONNECTION_FILENAME", None)
    timeout = float(args['--timeout'])
    tries = int(args['--retry'])
    notify = not args['--no-notify']
    timeout_wait = float(args['--timeout-wait'])
    wait = float(args['--wait'])
    debug = args["--debug"]


    configure_debug(debug)
    # plugins implement:
    #  match_connection: check connection profile is a possible hotspot (optional)
    #  match: check if the initial request is possibly the hotspot of the  plugin
    # accept: click the "accept AGB" button of the hotspot
    plugins = load("prisonbreak.plugins")

    if notify:
        log.info("Initializing notify")
        try:
            notify2.init('prison-break')
        except Exception as e:
            log.error("Error while initializing notify")
            log.error(e)

            log.info("For notifications to work, the DISPLAY and DBUS_SESSION_BUS_ADDRESS environment Variables must be set correctly (the logged in user). This is how they are currently set up :")
            log.info(f"DISPLAY={os.environ.get('DISPLAY')}")
            log.info(f"DBUS_SESSION_BUS_ADDRESS={os.environ.get('DBUS_SESSION_BUS_ADDRESS')}")
            notify=False
    note = functools.partial(send_notify,do_notify=notify)


    if args['--force-run']:
        log.info("CONNECTION_FILENAME environment is not set"
                  "and --force-run is set, assuming unconditional run")
    elif args['STATUS'] == 'down':
        log.info('device went down, doing nothing')
        exit(0)
    elif not profile:
        log.info("CONNECTION_FILENAME environment is not set"
                  ", assuming run as condition-change and doing nothing. Force with --force-run")
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
    if wait:
        log.info(f"Waiting for {wait} seconds before trying to connect")
        sleep(wait)

    for n in range(tries):
        try:
            initial_response = s.get(secret_url,timeout=timeout)
        except Timeout as t:
            log.info(f"Timeout number {n+1}, waiting {timeout_wait} seconds")
            continue
        except requests.exceptions.ConnectionError as t:
            log.info(f"Connection Error {n+1}, waiting {timeout_wait} seconds")
        else:
            log.debug(f"Success in try {n+1}")
            break
        sleep(timeout_wait)
    else:
        log.error(f'Unable to Retrieve the initial response after {tries} tires')
        exit(1)


    if initial_response.text.startswith("1337"):
        log.info("Received the correct challenge token"
                 ", assuming no captive portal")
        if args['--force-token']:
            log.info("Continuing even though we got the correct token!")
        else:
            exit(0)

    note("trying to connect with the available prison-break plugins",title="Prison-Break detected captive Portal!")
    for plug in plugins:
        name = plug.__name__
        sname = name.split(".")[-1]
        log.info(f"Running Plugin {name}")
        matched = plug.match(initial_response)
        if args['--force-match']:
            log.info("Force-match set, skipping plugin match."
                     f"Response would be {matched}")
        elif not matched:
            log.info(f"{name} cannot log into hotspot")
            continue
        note("Trying to accept AGBs for you now!",title=f"Prison-Break Plugin {name}")
        #notify2.Notification("Summary", "Some body text", "notification-message-im").show()
        if plug.accept(initial_response, s):
            log.info(f"{name} successful?")
            if s.get(secret_url,timeout=timeout).text.startswith("1337"):
                #notify2.Notification("Prison-Break", "Plugin {name} successful", "notification-message-im").show()

                log.info(f"{name} successful!")
                note("Managed to click you through the AGB captive portal.\nYou are now logged in!",title=f"Prison-Break Plugin {name}",timeout=20,critical=True)
                exit(0)
            else:
                #notify2.Notification("Prison-Break", "Plugin {name} tried to accept AGB but failed", "notification-message-im").show()
                log.warn(f"{name} failed to break free, continuing")
                note("Failed to log in, trying next plugin",title=f"Prison-Break Plugin {name}")

        else:
            log.info(f"{name} returned False, continuing")

    log.error("No plug was able to establish a connection")
    note("No Plugin was able to log through the captive portal, you will probably have to do it by hand, sorry!",title="Prison-Break failed",critical=True)


if __name__ == "__main__":
    main()
