# [M] Discourse: Duplicate lookup reveals restricted topic titles through canonicalized URLs

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-72722
Aliases: CVE-2026-72722, GHSA-4fx9-5m29-83p4
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72722
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, TopicLink.extract_from, TopicLink.ensure_entry_for, and TopicLink.duplicate_lookup do not consistently enforce Guardian.can_see? checks when processing internal links. An authenticated user can submit links to restricted topics, private messages, or hidden posts and receive canonicalized slugs or titles in the composer_messages duplicate_lookup response even though the targets are not visible to that user. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/commit/45abd925e46e8be40d2d047bced26628f26e4e31
- https://github.com/discourse/discourse/commit/7d7ce546ac86e24a6512b321ace69fc52fe37bf4
- https://github.com/discourse/discourse/commit/836a251d54a1004fb1c463a7d299b933b176191f
- https://github.com/discourse/discourse/commit/e54ba27eacee0f14f315e510e287e7ac2e4bdb1a
- https://github.com/discourse/discourse/pull/42091
- https://github.com/discourse/discourse/pull/42092
- https://github.com/discourse/discourse/pull/42093
- https://github.com/discourse/discourse/pull/42094
- https://github.com/discourse/discourse/security/advisories/GHSA-4fx9-5m29-83p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-72722
