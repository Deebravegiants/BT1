# [H] CVE-2020-24334

## Summary
Severity: High
Advisory: CVE-2020-24334
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24334
Type: osv

## Details
The code that processes DNS responses in uIP through 1.0, as used in Contiki and Contiki-NG, does not check whether the number of responses specified in the DNS packet header corresponds to the response data available in the DNS packet, leading to an out-of-bounds read and Denial-of-Service in resolv.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
