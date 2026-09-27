# [H] MZ Automation libIEC61850 NULL Pointer Dereference

## Summary
Severity: High
Advisory: CVE-2022-2973
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-2973
Type: osv

## Details
MZ Automation's libIEC61850 (versions 1.4 and prior; version 1.5 prior to commit a3b04b7bc4872a5a39e5de3fdc5fbde52c09e10e) uses a NULL pointer in certain situations. which could allow an attacker to crash the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2973.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2973
- https://www.cisa.gov/uscert/ics/advisories/icsa-22-251-01
