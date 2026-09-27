# [M] Discourse: Admin-only report can be exported by moderators

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32143
Aliases: CVE-2026-32143, GHSA-rhjf-mgqw-37wq
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32143
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, moderators could export CSV data for admin-restricted reports, bypassing the report visibility restrictions. This could expose sensitive operational data intended only for admins. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/727029a2983a14b50bce19439fbf9840db8372aa
- https://github.com/discourse/discourse/security/advisories/GHSA-rhjf-mgqw-37wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-32143
