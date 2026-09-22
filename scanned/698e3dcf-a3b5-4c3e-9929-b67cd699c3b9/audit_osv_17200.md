# [M] CVE-2020-13595

## Summary
Severity: Medium
Advisory: CVE-2020-13595
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-31
Source: https://osv.dev/vulnerability/CVE-2020-13595
Type: osv

## Details
The Bluetooth Low Energy (BLE) controller implementation in Espressif ESP-IDF 4.0 through 4.2 (for ESP32 devices) returns the wrong number of completed BLE packets and triggers a reachable assertion on the host stack when receiving a packet with an MIC failure. An attacker within radio range can silently trigger the assertion (which disables the target's BLE stack) by sending a crafted sequence of BLE packets.

## References
- https://asset-group.github.io/cves.html
- https://asset-group.github.io/disclosures/sweyntooth/
- https://github.com/espressif/esp32-bt-lib
