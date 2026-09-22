# [M] Insufficient validation of HTTPS and SVCB records

## Summary
Severity: Medium
Advisory: CVE-2026-33611
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-33611
Type: osv

## Details
An operator allowed to use the REST API can cause the Authoritative server to produce invalid HTTPS or SVCB record data, which can in turn cause LMDB database corruption, if using the LMDB backend.

## References
- https://repo.powerdns.com/
- https://docs.powerdns.com/authoritative/security-advisories/powerdns-advisory-powerdns-2026-05.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33611.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33611
- https://github.com/PowerDNS/pdns
