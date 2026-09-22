# [M] Local Mastodon users can enumerate and access severed relationships of every other local user

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-22246
Aliases: CVE-2026-22246, GHSA-ww85-x9cp-5v24
Ecosystem: Bitnami
Published: 2026-01-13
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-22246
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.4

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Mastodon 4.3 added notifications of severed relationships, allowing end-users to inspect the relationships they lost as the result of a moderation action. The code allowing users to download lists of severed relationships for a particular event fails to check the owner of the list before returning the lost relationships. Any registered local user can access the list of lost followers and followed users caused by any severance event, and go through all severance events this way. The leaked information does not include the name of the account which has lost follows and followers. This has been fixed in Mastodon v4.3.17, v4.4.11 and v4.5.4.

## References
- https://github.com/mastodon/mastodon/commit/68e30985ca7afdb89af1b2e9dc962e1993dc8076
- https://github.com/mastodon/mastodon/commit/b2bcd34486fd6681cc0f30028086ef0f47282adf
- https://github.com/mastodon/mastodon/commit/c1fb6893c5175d74c074f6f786d504c8bc610d57
- https://github.com/mastodon/mastodon/security/advisories/GHSA-ww85-x9cp-5v24
- https://nvd.nist.gov/vuln/detail/CVE-2026-22246
