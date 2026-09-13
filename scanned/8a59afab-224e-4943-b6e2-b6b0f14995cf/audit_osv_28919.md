# [M] MyFinances Allows Unauthorized Access to Other Customer Data

## Summary
Severity: Medium
Advisory: CVE-2024-37889
Aliases: GHSA-4884-3gvp-3wj2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37889
Type: osv

## Details
MyFinances is a web application for managing finances. MyFinances has a way to access other customer invoices while signed in as a user. This method allows an actor to access PII and financial information from another account. The vulnerability is fixed in 0.4.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37889.json
- https://github.com/TreyWW/MyFinances/security/advisories/GHSA-4884-3gvp-3wj2
- https://nvd.nist.gov/vuln/detail/CVE-2024-37889
- https://github.com/TreyWW/MyFinances/commit/2c1e6d5b7ec8b2d6f660b260e3c5f4d3eaaa613f
