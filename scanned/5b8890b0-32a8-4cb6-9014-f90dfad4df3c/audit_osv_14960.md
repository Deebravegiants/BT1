# [M] CVE-2019-12588

## Summary
Severity: Medium
Advisory: CVE-2019-12588
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-12588
Type: osv

## Details
The client 802.11 mac implementation in Espressif ESP8266_NONOS_SDK 2.2.0 through 3.1.0 does not validate correctly the RSN AuthKey suite list count in beacon frames, probe responses, and association responses, which allows attackers in radio range to cause a denial of service (crash) via a crafted message.

## References
- https://github.com/espressif
- https://github.com/Matheus-Garbelini/esp32_esp8266_attacks
- https://matheus-garbelini.github.io/home/post/esp8266-beacon-frame-crash/
