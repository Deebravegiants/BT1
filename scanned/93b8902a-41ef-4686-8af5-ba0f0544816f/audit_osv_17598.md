# [H] CVE-2020-17444

## Summary
Severity: High
Advisory: CVE-2020-17444
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17444
Type: osv

## Details
An issue was discovered in picoTCP 1.7.0. The routine for processing the next header field (and deducing whether the IPv6 extension headers are valid) doesn't check whether the header extension length field would overflow. Therefore, if it wraps around to zero, iterating through the extension headers will not increment the current data pointer. This leads to an infinite loop and Denial-of-Service in pico_ipv6_check_headers_sequence() in pico_ipv6.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
