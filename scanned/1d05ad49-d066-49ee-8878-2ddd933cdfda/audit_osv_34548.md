# [H] Anyquery Unauthenticated Access Vulnerability Exposes Private Integration Data

## Summary
Severity: High
Advisory: CVE-2025-61679
Aliases: GHSA-5f7p-rhmq-hvc7
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-10-03
Source: https://osv.dev/vulnerability/CVE-2025-61679
Type: osv

## Details
Anyquery is an SQL query engine built on top of SQLite. Versions 0.4.3 and below allow attackers who have already gained access to localhost, even with low privileges, to use the http server through the port unauthenticated, and access private integration data like emails, without any warning of a foreign login from the provider. This issue is fixed in version 0.4.4.

## References
- https://github.com/julien040/anyquery/releases/tag/0.4.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61679.json
- https://github.com/julien040/anyquery/security/advisories/GHSA-5f7p-rhmq-hvc7
- https://nvd.nist.gov/vuln/detail/CVE-2025-61679
- https://github.com/julien040/anyquery/commit/43cd8bd3354b9725b245a2354b08e1c9be1cc1d3
