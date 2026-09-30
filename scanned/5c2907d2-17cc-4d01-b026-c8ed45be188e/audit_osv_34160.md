# [C] aiven-db-migrate allows Privilege Escalation through use of psql during migration

## Summary
Severity: Critical
Advisory: CVE-2025-55283
Aliases: GHSA-wqhc-grmj-fjvg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-18
Source: https://osv.dev/vulnerability/CVE-2025-55283
Type: osv

## Details
aiven-db-migrate is an Aiven database migration tool. Prior to 1.0.7, there is a privilege escalation vulnerability that allows elevation to superuser inside PostgreSQL databases during a migration from an untrusted source server. The vulnerability stems from psql executing commands embedded in a dump from the source server. This vulnerability is fixed in 1.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55283.json
- https://github.com/aiven/aiven-db-migrate/security/advisories/GHSA-wqhc-grmj-fjvg
- https://nvd.nist.gov/vuln/detail/CVE-2025-55283
- https://github.com/aiven/aiven-db-migrate/commit/36f6c7f7d06216975f625da0a1cb514253c4b3df
