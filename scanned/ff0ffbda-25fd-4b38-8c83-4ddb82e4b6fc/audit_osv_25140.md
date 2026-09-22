# [C] CVE-2023-31470

## Summary
Severity: Critical
Advisory: CVE-2023-31470
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-31470
Type: osv

## Details
SmartDNS through 41 before 56d0332 allows an out-of-bounds write because of a stack-based buffer overflow in the _dns_encode_domain function in the dns.c file, via a crafted DNS request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31470.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31470
- https://github.com/pymumu/smartdns/issues/1378
- https://github.com/pymumu/smartdns/commit/56d0332bf91104cfc877635f6c82e9348587df04
