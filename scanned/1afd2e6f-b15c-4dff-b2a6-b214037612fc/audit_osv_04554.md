# [M] Discourse: Cross-site backup access via path traversal in multisite local backups

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-45775
Aliases: CVE-2026-45775, GHSA-5j6v-4x6g-9pg5
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-45775
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, a path traversal vulnerability in Discourse backup handling could allow an authenticated administrator on one site in a multisite deployment to access backup files belonging to another site when backups are stored locally. In affected configurations, an admin on Site A could potentially retrieve sensitive backup data from Site B (same host, multisite) by crafting a backup download request with a traversal payload. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-5j6v-4x6g-9pg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45775
