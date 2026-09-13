# [C] CVE-2020-24341

## Summary
Severity: Critical
Advisory: CVE-2020-24341
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24341
Type: osv

## Details
An issue was discovered in picoTCP and picoTCP-NG through 1.7.0. The TCP input data processing function in pico_tcp.c does not validate the length of incoming TCP packets, which leads to an out-of-bounds read when assembling received packets into a data segment, eventually causing Denial-of-Service or an information leak.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
