# [H] CVE-2020-17440

## Summary
Severity: High
Advisory: CVE-2020-17440
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-17440
Type: osv

## Details
An issue was discovered in uIP 1.0, as used in Contiki 3.0 and other products. The code that parses incoming DNS packets does not validate that domain names present in the DNS responses have '\0' termination. This results in errors when calculating the offset of the pointer that jumps over domain name bytes in DNS response packets when a name lacks this termination, and eventually leads to dereferencing the pointer at an invalid/arbitrary address, within newdata() and parse_name() in resolv.c.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
