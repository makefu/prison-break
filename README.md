# Prison Break from Captive Portals

Free yourself from the chains of having to acknowledging AGBs every time you connect to a captive portal.

## Usage

```
install -m755 -uroot prison-break /etc/NetworkManager/dispatcher.d/99prison-break
```

## Testing
The script will require `CONNECTION_PROFILE` to be set as it will read these
files to determine if we just connected to a potential captive portal
```
CONNECTION_FILENAME=profiles/WIFI@DB ./prison-break
```
