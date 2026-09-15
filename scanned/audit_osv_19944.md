# [M] CVE-2021-28136

## Summary
Severity: Medium
Advisory: CVE-2021-28136
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-28136
Type: osv

## Details
The Bluetooth Classic implementation in Espressif ESP-IDF 4.4 and earlier does not properly handle the reception of multiple LMP IO Capability Request packets during the pairing process, allowing attackers in radio range to trigger memory corruption (and consequently a crash) in ESP32 via a replayed (duplicated) LMP packet.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.espressif.com/en/products/socs/esp32
- https://github.com/espressif/esp-idf
- https://github.com/espressif/esp32-bt-lib
