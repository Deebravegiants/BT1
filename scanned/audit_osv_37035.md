# [M] Coolify: Cross-team deployment information disclosure via GET /api/v1/deployments/{uuid} (IDOR)

## Summary
Severity: Medium
Advisory: CVE-2026-27881
Aliases: GHSA-5p5w-h58c-2h5m
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-27881
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.464, `GET /api/v1/deployments/{uuid}` in DeployController.php retrieves deployment details without validating that the deployment belongs to the authenticated user's team. Any authenticated API user can read deployment records from other teams by providing a valid deployment UUID. This vulnerability is fixed in 4.0.0-beta.464.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27881.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-5p5w-h58c-2h5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-27881
