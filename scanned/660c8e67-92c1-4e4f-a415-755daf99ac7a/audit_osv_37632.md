# [H] Chartbrew Cross-Tenant Template Export and Secret Disclosure in `GET /team/:team_id/template/generate/:project_id`

## Summary
Severity: High
Advisory: CVE-2026-32252
Aliases: GHSA-mw4f-cf22-qpcj
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-32252
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. Prior to 4.9.0, a cross-tenant authorization bypass exists in Chartbrew in GET /team/:team_id/template/generate/:project_id. The GET handler calls checkAccess(req, "updateAny", "chart") without awaiting the returned promise, and it does not verify that the supplied project_id belongs to req.params.team_id or to the caller's team. As a result, an authenticated attacker with valid template-generation permissions in their own team can request the template model for a project belonging to another team and receive victim project data. This vulnerability is fixed in 4.9.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32252.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-mw4f-cf22-qpcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32252
- https://github.com/chartbrew/chartbrew/commit/bf5919043d3587fcbe76123aaabd9a0a9d1033f1
