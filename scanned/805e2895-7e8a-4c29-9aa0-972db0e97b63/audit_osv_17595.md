# [C] CVE-2020-17441

## Summary
Severity: Critical
Advisory: CVE-2020-17441
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17441
Type: osv

## Details
An issue was discovered in picoTCP 1.7.0. The code for processing the IPv6 headers does not validate whether the IPv6 payload length field is equal to the actual size of the payload, which leads to an Out-of-Bounds read during the ICMPv6 checksum calculation, resulting in either Denial-of-Service or Information Disclosure. This affects pico_ipv6_extension_headers and pico_checksum_adder (in pico_ipv6.c and pico_frame.c).

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
