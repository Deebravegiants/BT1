# [M] Arcane before 2.0.0 Missing Administrator Authorization on the Compose Template Mutation Endpoints

## Summary
Severity: Medium
Advisory: CVE-2026-86114
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86114
Type: osv

## Details
Arcane versions before 2.0.0 fail to properly restrict template operations, allowing default user role accounts to create, modify, and delete compose templates including instance-wide defaults. Attackers can inject malicious container configurations with privileged settings or host path mounts that execute with administrative privileges when deployed by administrators.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86114.json
- https://github.com/getarcaneapp/arcane/releases/tag/v2.0.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-86114
- https://www.vulncheck.com/advisories/arcane-before-2.0.0-missing-administrator-authorization-on-the-compose-template-mutation-endpoints
- https://github.com/getarcaneapp/arcane/commit/1500646aa91f
- https://github.com/getarcaneapp/arcane
- https://github.com/geo-chen/oss/blob/main/arcane.md
- https://github.com/getarcaneapp/arcane/blob/v1.19.5/backend/api/handlers/templates.go
