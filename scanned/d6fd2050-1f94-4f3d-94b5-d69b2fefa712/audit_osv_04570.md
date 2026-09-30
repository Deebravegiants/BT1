# [M] Discourse: Review queue exposes flag-related private message excerpts to category group moderators

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-59829
Aliases: CVE-2026-59829, GHSA-wmc6-pmxp-xw5w
Ecosystem: Bitnami
Published: 2026-08-21
Source: https://osv.dev/vulnerability/BIT-discourse-2026-59829
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.1, on sites with category group moderation enabled, the review queue could include an excerpt (and permalink) of the private message attached to a flag, even when the reviewing category moderator was not a participant in that message. These notify_moderators flag messages are addressed only to moderators and, for core flags, to a category's moderation groups as they existed when the flag was raised, so a category group moderator could read flag-discussion content they were not authorized to see. This affects official plugins that create such messages and core flags raised before a moderator's group was granted moderation of the category. Only the confidentiality of a limited excerpt of these flag-related private messages is affected; no content can be modified or deleted. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.1.

## References
- https://github.com/discourse/discourse/commit/4df0e54f59361c78606b578ad12a2c39b4dd9f59
- https://github.com/discourse/discourse/commit/58e45dc7c92d19d5294c73fbcd3833c73dc51754
- https://github.com/discourse/discourse/commit/74c8522a197658c69b0adefa182f601ce85dcefa
- https://github.com/discourse/discourse/commit/e56bd3ec58ae387946220821d1ce214eed02d1b9
- https://github.com/discourse/discourse/pull/41527
- https://github.com/discourse/discourse/security/advisories/GHSA-wmc6-pmxp-xw5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-59829
