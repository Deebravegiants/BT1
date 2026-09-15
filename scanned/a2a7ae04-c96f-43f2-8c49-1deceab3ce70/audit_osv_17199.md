# [M] CVE-2020-13594

## Summary
Severity: Medium
Advisory: CVE-2020-13594
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-31
Source: https://osv.dev/vulnerability/CVE-2020-13594
Type: osv

## Details
The Bluetooth Low Energy (BLE) controller implementation in Espressif ESP-IDF 4.2 and earlier (for ESP32 devices) does not properly restrict the channel map field of the connection request packet on reception, allowing attackers in radio range to cause a denial of service (crash) via a crafted packet.

## References
- https://asset-group.github.io/cves.html
- https://asset-group.github.io/disclosures/sweyntooth/
- https://github.com/espressif/esp32-bt-lib
