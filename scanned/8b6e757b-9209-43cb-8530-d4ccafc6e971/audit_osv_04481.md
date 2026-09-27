# [M] Discourse topic conversion permission vulnerability for moderators

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-21865
Aliases: CVE-2026-21865, GHSA-4777-wrv5-3g39
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2026-21865
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, moderators can convert some personal messages to public topics when they shouldn't have access. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. As a workaround, site admin can temporarily revoke the moderation role from untrusted moderators or remove the moderator group from the "personal message enabled groups" site setting until the Discourse instance has been upgraded to a version that has been patched.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-4777-wrv5-3g39
- https://nvd.nist.gov/vuln/detail/CVE-2026-21865
