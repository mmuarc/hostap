sudo cp orig.conf wpa_supplicant.conf

sudo ./wpa_supplicant -c wpa_supplicant.conf -i wlan1 -Dnl80211 -d | egrep "EAP:|EAP-NOOB"
