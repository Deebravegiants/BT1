# [M] CVE-2020-16150

## Summary
Severity: Medium
Advisory: CVE-2020-16150
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-02
Source: https://osv.dev/vulnerability/CVE-2020-16150
Type: osv

## Details
A Lucky 13 timing side channel in mbedtls_ssl_decrypt_buf in library/ssl_msg.c in Trusted Firmware Mbed TLS through 2.23.0 allows an attacker to recover secret key information. This affects CBC mode because of a computed time difference based on a padding length.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5OSOFUD6UTGTDDSQRS62BPXDU52I6PUA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IRPBHCQKZXHVKOP5O5EWE7P76AWGUXQJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OD3NM6GD73CTFFRBKG5G2ACXGG7QQHCC/
- https://tls.mbed.org/tech-updates/security-advisories
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2020-09-1
