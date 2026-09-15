# [H] CVE-2020-17468

## Summary
Severity: High
Advisory: CVE-2020-17468
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17468
Type: osv

## Details
An issue was discovered in FNET through 4.6.4. The code for processing the hop-by-hop header (in the IPv6 extension headers) doesn't check for a valid length of an extension header, and therefore an out-of-bounds read can occur in _fnet_ip6_ext_header_handler_options in fnet_ip6.c, leading to Denial-of-Service.

## References
- http://fnet.sourceforge.net/manual/fnet_history.html
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
