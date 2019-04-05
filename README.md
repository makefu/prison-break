# Prison Break from Captive Portals

Free yourself from the chains of having to acknowledging AGBs every time you connect to a captive portal.

## Installation

### NixOS
With NixOS 19.03 add to your `configuration.nix`:
```
{
  # .1 configure prison-break as dispatcher script
  networking.networkmanager.dispatcherScripts = [
    { source = "${nur.repos.makefu.prison-break}/bin/prison-break"; }
  ];

  # 2. Set up [NUR](https://github.com/nix-community/NUR/)
  nixpkgs.config.packageOverrides = pkgs: {
    nur = import (builtins.fetchTarball "https://github.com/nix-community/NUR/archive/master.tar.gz") {
      inherit pkgs;
    };
  };
}
```


### Legacy OS
If you have no problems working on a tainted system
```
python setup.py install
install -m755 -uroot /usr/bin/prison-break /etc/NetworkManager/dispatcher.d/99prison-break
```
## Testing
prison-break provides a couple of means to override the default behavior such
as providing a path to the `CONNECTION_FILENAME`:

```
prison-break --force-run   # do not bail out on missing CONNECTION_FILENAME
prison-break --force-token # continue even if the challenge token is correct
prison-break --force-match # contineu even if no plugin matched the connection profile as potential access point
```
## Logs

This is how a connection may look like for you when the script is started
via nm-dispatcher:
```
Apr 04 16:39:09 x nm-dispatcher[16291]: INFO:cli:CONNECTION_FILENAME set, checking if any plugin matches connection pattern
Apr 04 16:39:09 x nm-dispatcher[16291]: INFO:hotsplots:Unsecured wifi, might be hotsplots!
Apr 04 16:39:09 x nm-dispatcher[16291]: INFO:cli:at least one plugin matched Connection for being a possible AGB prison
Apr 04 16:39:11 x nm-dispatcher[16291]: INFO:cli:Running Plugin prisonbreak.plugins.hotsplots
Apr 04 16:39:11 x nm-dispatcher[16291]: INFO:hotsplots:Checking for hotsplots Portal
Apr 04 16:39:11 x nm-dispatcher[16291]: INFO:hotsplots:Got Redirected and follow http://192.168.44.1:80/logon?username=agb_accepted&response=14105ecbad6c2576a7746758fd76>
Apr 04 16:39:11 x nm-dispatcher[16291]: INFO:cli:prisonbreak.plugins.hotsplots successful?
Apr 04 16:39:12 x nm-dispatcher[16291]: INFO:cli:prisonbreak.plugins.hotsplots successful!
```

