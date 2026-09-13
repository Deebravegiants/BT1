# [H] CubeCart: Time-based Blind SQL Injection

## Summary
Severity: High
Advisory: CVE-2026-39358
Aliases: GHSA-8gj6-9fwc-h4gh
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-39358
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.6.0, Authenticated Time-Based Blind SQL Injection vulnerabilities were identified in the sorting parameters (sort[price], sort_activity, sort_admin, and sort_customer) of the Products and Logs endpoints in CubeCart v6.x. This allows an attacker to execute arbitrary SQL commands, compromising the confidentiality and integrity of the database. This vulnerability is fixed in 6.6.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39358.json
- https://github.com/cubecart/v6/security/advisories/GHSA-8gj6-9fwc-h4gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-39358
