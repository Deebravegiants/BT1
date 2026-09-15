# [M] Metabase before 0.63.1 Missing Function-Level Authorization on the Glossary Management API

## Summary
Severity: Medium
Advisory: CVE-2026-86116
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86116
Type: osv

## Details
Metabase versions before 0.63.1 fail to enforce data analyst permission checks on glossary API endpoints, allowing any authenticated user to create, modify, and delete glossary entries. Attackers can submit requests to POST, PUT, and DELETE glossary endpoints to tamper with instance-wide business glossary data without proper authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86116.json
- https://github.com/metabase/metabase/releases/tag/v0.63.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-86116
- https://www.vulncheck.com/advisories/metabase-before-0.63.1-missing-function-level-authorization-on-the-glossary-management-api
- https://github.com/metabase/metabase/commit/0a0589299cfd
- https://github.com/metabase/metabase
- https://github.com/geo-chen/oss/blob/main/metabase.md
- https://github.com/metabase/metabase/blob/v0.62.1/src/metabase/glossary/api.clj
