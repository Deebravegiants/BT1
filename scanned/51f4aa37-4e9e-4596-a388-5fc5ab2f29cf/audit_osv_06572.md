# [M] Mastadon streaming server allows OAuth clients without the `read` scope to subscribe to public channels

## Summary
Severity: Medium
Advisory: BIT-mastodon-2025-62176
Aliases: CVE-2025-62176, GHSA-7gwh-mw97-qjgp
Ecosystem: Bitnami
Published: 2025-10-15
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-62176
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.4.0 <4.4.6

## Details
Mastodon is a free, open-source social network server based on ActivityPub. In Mastodon before 4.4.6, 4.3.14, and 4.2.27, the streaming server accepts serving events for public timelines to clients using any valid authentication token, even if those tokens lack the read:statuses scope. This allows OAuth clients without the read scope to subscribe to public channels and receive public timeline events. The impact is limited, as this only affects new public posts published on the public timelines and requires an otherwise valid token, but this may lead to unexpected access to public posts in a limited-federation setting. This issue has been patched in versions 4.4.6, 4.3.14, and 4.2.27. No known workarounds exist.

## References
- https://github.com/mastodon/mastodon/commit/7e98fa9b476fdaed235519f1d527eb956004ba0c
- https://github.com/mastodon/mastodon/security/advisories/GHSA-7gwh-mw97-qjgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-62176
