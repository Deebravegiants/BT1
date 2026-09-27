# [M] CVE-2021-28135

## Summary
Severity: Medium
Advisory: CVE-2021-28135
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-28135
Type: osv

## Details
The Bluetooth Classic implementation in Espressif ESP-IDF 4.4 and earlier does not properly handle the reception of continuous unsolicited LMP responses, allowing attackers in radio range to trigger a denial of service (crash) in ESP32 by flooding the target device with LMP Feature Response data.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.espressif.com/en/products/socs/esp32
- https://github.com/espressif/esp-idf
- https://github.com/espressif/esp32-bt-lib
