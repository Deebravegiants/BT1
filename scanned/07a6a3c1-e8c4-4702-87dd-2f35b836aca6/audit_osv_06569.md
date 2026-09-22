# [M] Mastodon's domain blocks & rationales ignore user approval when visibility set as "users"

## Summary
Severity: Medium
Advisory: BIT-mastodon-2025-27399
Aliases: CVE-2025-27399, GHSA-94h4-fj37-c825
Ecosystem: Bitnami
Published: 2025-03-02
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-27399
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=0 <4.3.4

## Details
Mastodon is a self-hosted, federated microblogging platform. In versions prior to 4.1.23, 4.2.16, and 4.3.4, when the visibility for domain blocks/reasons is set to "users" (localized English string: "To logged-in users"), users that are not yet approved can view the block reasons. Instance admins that do not want their domain blocks to be public are impacted. Versions 4.1.23, 4.2.16, and 4.3.4 fix the issue.

## References
- https://github.com/mastodon/mastodon/blob/93f0427b8a84faf68d5d02cdf9a26f98fae16f2b/app/controllers/api/v1/instances/domain_blocks_controller.rb#L33-L35
- https://github.com/mastodon/mastodon/blob/93f0427b8a84faf68d5d02cdf9a26f98fae16f2b/app/controllers/api/v1/instances/domain_blocks_controller.rb#L49-L51
- https://github.com/mastodon/mastodon/commit/6b519cfefa93a923b19d0f20c292c7185f8fd5f5
- https://github.com/mastodon/mastodon/security/advisories/GHSA-94h4-fj37-c825
- https://nvd.nist.gov/vuln/detail/CVE-2025-27399
