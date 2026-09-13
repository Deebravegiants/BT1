# [H] CVE-2020-17445

## Summary
Severity: High
Advisory: CVE-2020-17445
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17445
Type: osv

## Details
An issue was discovered in picoTCP 1.7.0. The code for processing the IPv6 destination options does not check for a valid length of the destination options header. This results in an Out-of-Bounds Read, and, depending on the memory protection mechanism, this may result in Denial-of-Service in pico_ipv6_process_destopt() in pico_ipv6.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
