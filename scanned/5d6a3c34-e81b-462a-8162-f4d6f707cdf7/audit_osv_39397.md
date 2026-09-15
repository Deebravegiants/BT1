# [H] Nextcloud: SQL Injection in Column Type Parameter Allows Arbitrary SQL Execution

## Summary
Severity: High
Advisory: CVE-2026-45545
Aliases: GHSA-x43f-gmgh-vvjj
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45545
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From versions 0.7.0 to before 0.7.7, 0.8.0 to before 0.8.10, 0.9.0 to before 0.9.8, and 1.0.0 to before 1.0.4, an authenticated attacker with access to the Tables app may be able to execute arbitrary up to 20 bytes long SQL queries, through a stored injection. With carefully crafted input it is possible to break out of the length limitation. The attacker could use this to extract information from the database, or modify data. This issue has been patched in versions 0.7.7, 0.8.10, 0.9.8, 1.0.4, and 2.0.0.

## References
- https://hackerone.com/reports/3462991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45545.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-x43f-gmgh-vvjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-45545
- https://github.com/nextcloud/tables/pull/2309
