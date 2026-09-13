# [M] Off-by-one access when processing crafted UDP responses

## Summary
Severity: Medium
Advisory: CVE-2026-33602
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33602
Type: osv

## Details
A rogue backend can send a crafted UDP response with a query ID off by one related to the maximum configured value, triggering an out-of-bounds write leading to a denial of service.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33602.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33602
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-04.html
- https://github.com/PowerDNS/pdns
