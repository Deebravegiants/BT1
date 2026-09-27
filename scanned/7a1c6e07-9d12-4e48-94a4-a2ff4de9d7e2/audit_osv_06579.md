# [M] Mastodon has insufficient access control to push notification settings

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-23964
Aliases: CVE-2026-23964, GHSA-f3q8-7vw3-69v4
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-23964
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.5

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to versions 4.5.5, 4.4.12, and 4.3.18, an insecure direct object reference in the web push subscription update endpoint lets any authenticated user update another user's push subscription by guessing or obtaining the numeric subscription id. This can be used to disrupt push notifications for other users and also leaks the web push subscription endpoint. Any user with a web push subscription is impacted, because another authenticated user can tamper with their push subscription settings if they can guess or obtain the subscription id. This allows an attacker to disrupt push notifications by changing the policy (whether to filter notifications from non-followers or non-followed users) and subscribed notification types of their victims. Additionally, the endpoint returns the subscription object, which includes the push notification endpoint for this subscription, but not its keypair. Mastodon versions v4.5.5, v4.4.12, v4.3.18 are patched.

## References
- https://github.com/mastodon/mastodon/releases/tag/v4.3.18
- https://github.com/mastodon/mastodon/releases/tag/v4.4.12
- https://github.com/mastodon/mastodon/releases/tag/v4.5.5
- https://github.com/mastodon/mastodon/security/advisories/GHSA-f3q8-7vw3-69v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-23964
