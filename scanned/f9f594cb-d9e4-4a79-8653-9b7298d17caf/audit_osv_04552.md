# [H] Discourse: Signup-time primary_group_id assignment grants whisperer access

## Summary
Severity: High
Advisory: BIT-discourse-2026-44787
Aliases: CVE-2026-44787, GHSA-vmwq-jvxx-jwfx
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44787
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, the signup flow could allow newly registered users to set primary_group_id and gain whisper-group privileges without legitimate group membership on sites with whispers_allowed_groups configured. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/012796ac28c85b30aa233c5ef042fc66efff8126
- https://github.com/discourse/discourse/commit/0f50a07a6ef4b33f3f826ce6d7bf6d7bd16912d8
- https://github.com/discourse/discourse/commit/5418e3027dba109e27a4796463686d61e190ac29
- https://github.com/discourse/discourse/commit/6fc7e6cf04422fc3f9d1c99134803071e983ff0a
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-vmwq-jvxx-jwfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44787
