# [M] Discourse: Composer mentions endpoint leaks hidden group membership through PM `allowed_names` check

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-31869
Aliases: CVE-2026-31869, GHSA-5f9h-vp7v-7vq5
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-31869
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, the ComposerController#mentions endpoint reveals hidden group membership to any authenticated user who can message the group. By supplying allowed_names referencing a hidden-membership group and probing arbitrary usernames, an attacker can infer membership based on whether user_reasons returns "private" for a given user. This bypasses group member-visibility controls. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch. To work around this issue, restrict the messageable policy of any hidden-membership group to staff or group members only, so untrusted users cannot reach the vulnerable code path.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-5f9h-vp7v-7vq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-31869
