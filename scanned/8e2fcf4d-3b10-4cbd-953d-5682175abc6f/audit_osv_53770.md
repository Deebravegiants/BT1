# [M] CVE-2023-24023

## Summary
Severity: Medium
Advisory: CVE-2023-24023
Aliases: A-255601934, ASB-A-255601934
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-11-28
Source: https://osv.dev/vulnerability/CVE-2023-24023
Type: osv

## Details
Bluetooth BR/EDR devices with Secure Simple Pairing and Secure Connections pairing in Bluetooth Core Specification 4.2 through 5.4 allow certain man-in-the-middle attacks that force a short key length, and might lead to discovery of the encryption key and live injection, aka BLUFFS.

## References
- https://dl.acm.org/doi/10.1145/3576915.3623066
- https://www.bluetooth.com/learn-about-bluetooth/key-attributes/bluetooth-security/bluffs-vulnerability/
