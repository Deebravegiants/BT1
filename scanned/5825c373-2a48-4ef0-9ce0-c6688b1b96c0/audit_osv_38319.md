# [M] CVE-2026-38587

## Summary
Severity: Medium
Advisory: CVE-2026-38587
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-38587
Type: osv

## Details
An Insecure Direct Object Reference (IDOR) vulnerability was discovered in ONLYOFFICE DocSpace before 3.2.1. The flaw exists in multiple REST API endpoints. This allows authenticated users with low-level permissions (User or Guest) to retrieve sensitive information, such as the Owner's unique identifier (ID) and profile information, which should only be accessible to administrators.

## References
- https://github.com/ONLYOFFICE/DocSpace/blob/master/CHANGELOG.md#security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38587.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38587
