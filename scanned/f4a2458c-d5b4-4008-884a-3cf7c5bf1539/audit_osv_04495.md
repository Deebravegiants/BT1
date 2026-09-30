# [M] Discourse: Hidden tag visibility bypass on tag routes

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27481
Aliases: CVE-2026-27481, GHSA-6c9x-3vrp-682x
Ecosystem: Bitnami
Published: 2026-04-08
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27481
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, an authorization bypass vulnerability allows unauthenticated or unauthorized users to view hidden (staff-only) tags and its associated data. All Discourse instances with tagging enabled and staff-only tag groups configured are impacted. This issue has been patched in versions 2026.1.3 and 2026.2.2.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-6c9x-3vrp-682x
- https://nvd.nist.gov/vuln/detail/CVE-2026-27481
