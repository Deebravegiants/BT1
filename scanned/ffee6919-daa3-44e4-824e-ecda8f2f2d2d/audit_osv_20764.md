# [H] CVE-2021-36754

## Summary
Severity: High
Advisory: CVE-2021-36754
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-36754
Type: osv

## Details
PowerDNS Authoritative Server 4.5.0 before 4.5.1 allows anybody to crash the process by sending a specific query (QTYPE 65535) that causes an out-of-bounds exception.

## References
- http://www.openwall.com/lists/oss-security/2021/07/26/2
- https://doc.powerdns.com/authoritative/security-advisories/index.html
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2021-01.html
