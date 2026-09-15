# [H] CVE-2021-28139

## Summary
Severity: High
Advisory: CVE-2021-28139
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-28139
Type: osv

## Details
The Bluetooth Classic implementation in Espressif ESP-IDF 4.4 and earlier does not properly restrict the Feature Page upon reception of an LMP Feature Response Extended packet, allowing attackers in radio range to trigger arbitrary code execution in ESP32 via a crafted Extended Features bitfield payload.

## References
- https://dl.packetstormsecurity.net/papers/general/braktooth.pdf
- https://www.espressif.com/en/products/socs/esp32
- https://github.com/espressif/esp-idf
- https://github.com/espressif/esp32-bt-lib
