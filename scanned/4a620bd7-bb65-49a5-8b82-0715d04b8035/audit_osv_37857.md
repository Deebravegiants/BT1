# [M] Null pointer dereference in RPZ transfer

## Summary
Severity: Medium
Advisory: CVE-2026-33600
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33600
Type: osv

## Details
An RPZ sent by a malicious authoritative server can result in a null pointer dereference, caused by a missing consistency check and leading to a denial of service.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-powerdns-2026-03.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33600.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33600
- https://github.com/PowerDNS/pdns
