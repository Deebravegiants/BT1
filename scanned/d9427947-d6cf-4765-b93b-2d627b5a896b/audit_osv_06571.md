# [M] Mastodon streaming API fails to disconnect disabled and suspended users

## Summary
Severity: Medium
Advisory: BIT-mastodon-2025-62175
Aliases: CVE-2025-62175, GHSA-r2fh-jr9c-9pxh
Ecosystem: Bitnami
Published: 2025-10-15
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-62175
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.4.0 <4.4.6

## Details
Mastodon is a free, open-source social network server based on ActivityPub. In versions before 4.4.6, 4.3.14, and 4.2.27, disabling or suspending a user account does not disconnect the account from the streaming API. This allows disabled or suspended accounts to continue receiving real-time updates through existing streaming connections and to establish new streaming connections, even though they cannot interact with other API endpoints. This undermines moderation actions, as administrators expect disabled or suspended accounts to be fully disconnected from the service. This issue has been patched in versions 4.4.6, 4.3.14, and 4.2.27. No known workarounds exist.

## References
- https://github.com/mastodon/mastodon/commit/2971ac9863b91372e68ac152caf6f4dbff511d17
- https://github.com/mastodon/mastodon/security/advisories/GHSA-r2fh-jr9c-9pxh
- https://nvd.nist.gov/vuln/detail/CVE-2025-62175
