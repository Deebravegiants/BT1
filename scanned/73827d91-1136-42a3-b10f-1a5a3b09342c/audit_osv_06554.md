# [M] BIT-mastodon-2022-48364

## Summary
Severity: Medium
Advisory: BIT-mastodon-2022-48364
Aliases: CVE-2022-48364
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2022-48364
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=3.5.0 <3.5.3

## Details
The undo_mark_statuses_as_sensitive method in app/services/approve_appeal_service.rb in Mastodon 3.5.x before 3.5.3 does not use the server's representative account, resulting in moderator identity disclosure when a moderator approves the appeal of a user whose status update was marked as sensitive.

## References
- https://github.com/40826d/advisories/blob/master/CVE-2022-48364/README.md
- https://github.com/mastodon/mastodon/blob/main/CHANGELOG.md#353---2022-05-26
- https://github.com/mastodon/mastodon/compare/v3.5.2...v3.5.3
- https://github.com/mastodon/mastodon/pull/18525
- https://nvd.nist.gov/vuln/detail/CVE-2022-48364
