# [M] Nextcloud Server users can modify tags on files that do not belong to them

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2025-66547
Aliases: CVE-2025-66547, GHSA-hq6c-r898-fgf2
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2025-66547
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <31.0.1

## Details
Nextcloud Server is a self hosted personal cloud system. In Nextcloud Server and Enterprise Server prior to 31.0.1, non-privileged users can modify tags on files they should not have access to via bulk tagging. This vulnerability is fixed in 31.0.1.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-hq6c-r898-fgf2
- https://github.com/nextcloud/server/commit/b44f1568f2dc97c746281d99e2342ad679e3d8a9
- https://github.com/nextcloud/server/issues/51247
- https://github.com/nextcloud/server/pull/51288
- https://hackerone.com/reports/3040887
- https://nvd.nist.gov/vuln/detail/CVE-2025-66547
