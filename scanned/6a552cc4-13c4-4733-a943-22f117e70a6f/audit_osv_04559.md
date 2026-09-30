# [M] Discourse: Don't leak restricted tag group names via tag info

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-47264
Aliases: CVE-2026-47264, GHSA-4q5q-6hh6-53x2
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-47264
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, DetailedTagSerializer#tag_group_names returned every tag group a tag belonged to without filtering against the requesting user's visibility. With SiteSetting.tags_listed_by_group enabled, anonymous and unprivileged users hitting TagsController#info (which is exempt from requires_login) could read the names of tag groups restricted to specific user groups or non-visible categories. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-4q5q-6hh6-53x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-47264
