# [M] Discourse: Missing post-level authorization allows whisper metadata disclosure

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32620
Aliases: CVE-2026-32620, GHSA-xgg2-vwr6-2c65
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32620
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, non-staff users could access read receipt information for staff-only posts they weren't supposed to see. No post content was exposed, only metadata about who read the post and when. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/bf8dbf6155ae483245d42a0164181bc226af674d
- https://github.com/discourse/discourse/security/advisories/GHSA-xgg2-vwr6-2c65
- https://nvd.nist.gov/vuln/detail/CVE-2026-32620
