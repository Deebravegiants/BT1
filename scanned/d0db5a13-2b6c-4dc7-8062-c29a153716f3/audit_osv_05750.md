# [M] CVE-2026-11817 CVE Record

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-11817
Aliases: CVE-2026-11817
Ecosystem: Bitnami
Published: 2026-08-21
Source: https://osv.dev/vulnerability/BIT-grafana-2026-11817
Type: osv

## Affected
- Bitnami: `grafana` — affected >=0 <13.1.1

## Details
This vulnerability only affects Grafana stacks configured with multiple organizations; single-organization deployments are not impacted. In a multi-organization stack, a user who is an Org Admin of a single organization can call GET /api/access-control/users/permissions/search?actionPrefix=dashboards: and receive permission data belonging to other organizations. The disclosed data is limited to dashboard and folder identifiers (UIDs) and per-user permission/scope mappings (which user holds which access on which dashboard). Dashboard contents, panels, query results, datasource credentials, secrets, and personal data are not exposed. This is a limited cross-organization information disclosure affecting multi-org deployments only.

## References
- https://grafana.com/security/security-advisories/cve-2026-11817
- https://nvd.nist.gov/vuln/detail/CVE-2026-11817
