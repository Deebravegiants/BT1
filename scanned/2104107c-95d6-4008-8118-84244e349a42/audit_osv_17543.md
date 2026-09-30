# [H] CVE-2020-16146

## Summary
Severity: High
Advisory: CVE-2020-16146
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/CVE-2020-16146
Type: osv

## Details
Espressif ESP-IDF 2.x, 3.0.x through 3.0.9, 3.1.x through 3.1.7, 3.2.x through 3.2.3, 3.3.x through 3.3.2, and 4.0.x through 4.0.1 has a Buffer Overflow in BluFi provisioning in btc_blufi_recv_handler function in blufi_prf.c. An attacker can send a crafted BluFi protocol Write Attribute command to characteristic 0xFF01. With manipulated packet fields, there is a buffer overflow.

## References
- https://github.com/espressif/esp-idf
- https://github.com/pokerfacett/MY_CVE_CREDIT/blob/master/CVE-2020-16146.md
