# [H] CVE-2020-24337

## Summary
Severity: High
Advisory: CVE-2020-24337
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24337
Type: osv

## Details
An issue was discovered in picoTCP and picoTCP-NG through 1.7.0. When an unsupported TCP option with zero length is provided in an incoming TCP packet, it is possible to cause a Denial-of-Service by achieving an infinite loop in the code that parses TCP options, aka tcp_parse_options() in pico_tcp.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
