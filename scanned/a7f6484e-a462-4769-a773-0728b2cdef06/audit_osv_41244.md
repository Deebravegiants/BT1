# [H] grav-plugin-database: SQL Injection in PDO::tableExists() due to Unsanitized Table Name Interpolation

## Summary
Severity: High
Advisory: CVE-2026-58492
Aliases: GHSA-8jxg-4pw9-xcwf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-58492
Type: osv

## Details
grav-plugin-database is the database plugin for Grav CMS. Prior to 1.2.0, the PDO::tableExists method interpolates its table argument directly into a raw SQL query string without sanitization, escaping, quoting, or whitelisting, allowing attacker-controlled table names passed by consuming plugin or developer code to execute arbitrary SQL against the configured database. This issue is fixed in version 1.2.0.

## References
- https://github.com/getgrav/grav-plugin-database/releases/tag/1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58492.json
- https://github.com/getgrav/grav/security/advisories/GHSA-8jxg-4pw9-xcwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-58492
- https://github.com/getgrav/grav-plugin-database/commit/f6d058785c9e23df7efc5ea7556f8746fef286df
