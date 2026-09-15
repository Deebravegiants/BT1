# [C] Metacat has an unauthenticated SQL injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-48114
Aliases: GHSA-wrc6-rc34-hrcg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2026-48114
Type: osv

## Details
Metacat is data repository software that helps researchers preserve, share, and discover data. Versions 2.0.0 and and above contain an unauthenticated SQL injection in the /harvesterRegistration endpoint. HarvesterRegistration.dbInsert() builds an INSERT against HARVEST_SITE_SCHEDULE via string concatenation, using a quoteString() helper that performs raw single-quote wrapping without escaping. Three request parameters reach the sink: unit, contactEmail, and documentListURL. The servlet does not verify a real LDAP identity. Allowing the vulnerable insert to proceed. Since the PostgreSQL backend permits stacked queries via Statement.executeUpdate(), this vulnerability allows full read/write/execute access in the Metacat database context. The vulnerability was remediated in Metacat 3.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48114.json
- https://github.com/NCEAS/metacat/security/advisories/GHSA-wrc6-rc34-hrcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-48114
- https://github.com/NCEAS/metacat/commit/820d595309b399fdbdf4983bd1b1dd795773472a
