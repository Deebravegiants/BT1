# [M] CVE-2020-17470

## Summary
Severity: Medium
Advisory: CVE-2020-17470
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17470
Type: osv

## Details
An issue was discovered in FNET through 4.6.4. The code that initializes the DNS client interface structure does not set sufficiently random transaction IDs (they are always set to 1 in _fnet_dns_poll in fnet_dns.c). This significantly simplifies DNS cache poisoning attacks.

## References
- http://fnet.sourceforge.net/manual/fnet_history.html
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
