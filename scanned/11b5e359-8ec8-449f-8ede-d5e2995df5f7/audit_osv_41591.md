# [H] Kamaji: TenantControlPlane namespace/name collision binds two tenants to the same SQL datastore schema + DB user, breaking per-tenant isolation

## Summary
Severity: High
Advisory: CVE-2026-62246
Aliases: GHSA-4f3f-65vx-r34f
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-62246
Type: osv

## Details
Kamaji is the Hosted Control Plane Manager for Kubernetes. Prior to 26.7.4-edge, Kamaji derives a TenantControlPlane datastore schema, database user, and etcd key prefix from a lossy namespace-and-name normalization in GetDefaultDatastoreSchema() and GetDefaultDatastoreUsername(), allowing distinct tenants with colliding normalized identifiers to share control-plane state and read, modify, or destroy another tenant's Kubernetes data. This issue is fixed in version 26.7.4-edge.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62246.json
- https://github.com/clastix/kamaji/security/advisories/GHSA-4f3f-65vx-r34f
- https://nvd.nist.gov/vuln/detail/CVE-2026-62246
- https://github.com/clastix/kamaji/commit/4232a9df7ccd08075c26191f59566202042543a9
