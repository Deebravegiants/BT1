# [H] CVE-2020-17442

## Summary
Severity: High
Advisory: CVE-2020-17442
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17442
Type: osv

## Details
An issue was discovered in picoTCP 1.7.0. The code for parsing the hop-by-hop IPv6 extension headers does not validate the bounds of the extension header length value, which may result in Integer Wraparound. Therefore, a crafted extension header length value may cause Denial-of-Service because it affects the loop in which the extension headers are parsed in pico_ipv6_process_hopbyhop() in pico_ipv6.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
