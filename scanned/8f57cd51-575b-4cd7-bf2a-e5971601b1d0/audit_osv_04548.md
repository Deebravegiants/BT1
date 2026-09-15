# [M] Discourse: Replying to a whisper lets non-whisperers create staff-only whisper posts

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44783
Aliases: CVE-2026-44783, GHSA-98ch-mgfj-wqpw
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44783
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, a flaw in how replies to whisper posts are handled allows authenticated users outside the groups configured in whispers_allowed_groups to post into a topic's staff-only whisper channel. The injected content is visible to whisperers (typically staff) alongside legitimate whispers. Only sites that have whispers enabled are affected. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-98ch-mgfj-wqpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44783
