# [H] ZITADEL Cross-Tenant Information Disclosure in Management API

## Summary
Severity: High
Advisory: CVE-2026-32131
Aliases: GHSA-wr6r-59xg-4pj2
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32131
Type: osv

## Details
ZITADEL is an open source identity management platform. Prior to 3.4.8 and 4.12.2, a vulnerability in Zitadel's Management API has been reported, which allowed authenticated users holding a valid low-privilege token (e.g., project.read, project.grant.read, or project.app.read) to retrieve management-plane information belonging to other organizations by specifying a different tenant’s project_id, grant_id, or app_id. This vulnerability is fixed in 3.4.8 and 4.12.2.

## References
- https://github.com/zitadel/zitadel/releases/tag/v3.4.8
- https://github.com/zitadel/zitadel/releases/tag/v4.12.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32131.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-wr6r-59xg-4pj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32131
