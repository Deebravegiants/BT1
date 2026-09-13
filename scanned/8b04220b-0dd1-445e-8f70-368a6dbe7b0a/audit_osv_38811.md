# [M] Insufficient input validation in ZoneToCache

## Summary
Severity: Medium
Advisory: CVE-2026-42387
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-42387
Type: osv

## Details
A malicious authoritative server can send a crafted zone via the ZoneToCache function that leads to a crash of the Recursor due to insuffcient input validation.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-08.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42387
- https://github.com/PowerDNS/pdns
