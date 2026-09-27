# [M] Discourse has a bypass of official warnings messages by non-staff users

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27491
Aliases: CVE-2026-27491, GHSA-xq37-5fvf-4m4j
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27491
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, a type coercion issue in a post actions API endpoint allowed non-staff users to issue warnings to other users. Warnings are a staff-only moderation feature. The vulnerability required the attacker to be a logged-in user and to send a specifically crafted request. No data exposure or privilege escalation beyond the ability to create unauthorized user warnings was possible. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/60a588f4da4ab0feceb2c44787d4261b4f8757be
- https://github.com/discourse/discourse/commit/d3cb203feabc46d765ecb91f348613a2bd531b89
- https://github.com/discourse/discourse/commit/f5fef73827da7520efc517357bd2a6bab35d7886
- https://github.com/discourse/discourse/security/advisories/GHSA-xq37-5fvf-4m4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-27491
