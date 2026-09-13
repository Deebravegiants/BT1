# [M] Discourse: Hidden reply-to post raw can be disclosed through AI explain prompts

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44785
Aliases: CVE-2026-44785, GHSA-7h76-fwxc-j586
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44785
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, the AI "explain" helper only checks can_see? on the post being explained, not its reply_to_post, so any authenticated user with access to the AI helper could read the raw contents of a hidden parent post by invoking "Explain" on a reply to it. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-7h76-fwxc-j586
- https://nvd.nist.gov/vuln/detail/CVE-2026-44785
