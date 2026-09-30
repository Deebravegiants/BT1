# [M] Discourse hasUnauthorized Exposure of Private User Action Types

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-30891
Aliases: CVE-2026-30891, GHSA-ww5f-24g5-c33g
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-30891
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, a user could access another user's private activity due to insufficient authorization checks in the user actions endpoint. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-ww5f-24g5-c33g
- https://nvd.nist.gov/vuln/detail/CVE-2026-30891
