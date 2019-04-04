# Prison Break from Captive Portals

Free yourself from the chains of having to acknowledging AGBs every time you connect to a captive portal.

## Installation

### NixOS
After installing [NUR](https://github.com/nix-community/NUR/)
```
{
  networking.networkmanager.dispatcherScripts = [
    { source = "${nur.repos.makefu.prison-break}/bin/prison-break"; }
  ];
}
```

### Legacy OS
If you have no problems working on a tainted system
```
python setup.py install
install -m755 -uroot /usr/bin/prison-break /etc/NetworkManager/dispatcher.d/99prison-break
```
