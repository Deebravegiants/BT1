# [M] DoQ/DoH3 excessive memory allocation

## Summary
Severity: Medium
Advisory: CVE-2026-33595
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33595
Type: osv

## Details
A client can trigger excessive memory allocation by generating a lot of errors responses over a single DoQ and DoH3 connection, as some resources were not properly released until the end of the connection.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33595.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33595
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-04.html
- https://github.com/PowerDNS/pdns
