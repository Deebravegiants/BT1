# [C] CVE-2018-17317

## Summary
Severity: Critical
Advisory: CVE-2018-17317
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-17317
Type: osv

## Details
FruityWifi (aka PatatasFritas/PatataWifi) 2.1 allows remote attackers to execute arbitrary commands via shell metacharacters in the io_mode, ap_mode, io_action, io_in_iface, io_in_set, io_in_ip, io_in_mask, io_in_gw, io_out_iface, io_out_set, io_out_mask, io_out_gw, iface, or domain parameter to /www/script/config_iface.php, or the newSSID, hostapd_secure, hostapd_wpa_passphrase, or supplicant_ssid parameter to /www/page_config.php.

## References
- https://github.com/xtr4nge/FruityWifi/issues/276
- http://blog.51cto.com/010bjsoft/2175710
- https://github.com/PatatasFritas/PatataWifi/issues/1
