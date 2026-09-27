# [H] Incomplete domain name sanitization during

## Summary
Severity: High
Advisory: CVE-2026-33608
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33608
Type: osv

## Details
An attacker can send a notify request that causes a new secondary domain to be added to the bind backend, but causes said backend to update its configuration to an invalid one, leading to the backend no longer able to run on the next restart, requiring manual operation to fix it.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/authoritative/security-advisories/powerdns-advisory-powerdns-2026-05.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33608.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33608
- https://github.com/PowerDNS/pdns
