# [H] Tarkov Data Manager has Authenticated SQL Injection

## Summary
Severity: High
Advisory: CVE-2026-21856
Aliases: GHSA-4gcx-ghwc-rc78
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21856
Type: osv

## Details
The Tarkov Data Manager is a tool to manage the Tarkov item data. Prior to commit 9bdb3a75a98a7047b6d70144eb1da1655d6992a8, a time based blind SQL injection vulnerability in the webhook edit and scanner api endpoints that allow an authenticated attacker to execute arbitrary SQL queries against the MySQL database. Commit 9bdb3a75a98a7047b6d70144eb1da1655d6992a8 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21856.json
- https://github.com/the-hideout/tarkov-data-manager/security/advisories/GHSA-4gcx-ghwc-rc78
- https://nvd.nist.gov/vuln/detail/CVE-2026-21856
- https://github.com/the-hideout/tarkov-data-manager/commit/9bdb3a75a98a7047b6d70144eb1da1655d6992a8
