# [H] Mastodon e‑mail throttle misconfiguration allows unlimited email confirmations against unconfirmed emails

## Summary
Severity: High
Advisory: BIT-mastodon-2025-54879
Aliases: CVE-2025-54879, GHSA-84ch-6436-c7mg
Ecosystem: Bitnami
Published: 2025-08-08
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-54879
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.4.0 <4.4.3

## Details
Mastodon is a free, open-source social network server based on ActivityPub Mastodon which facilitates LDAP configuration for authentication. In versions 3.1.5 through 4.2.24, 4.3.0 through 4.3.11 and 4.4.0 through 4.4.3, Mastodon's rate-limiting system has a critical configuration error where the email-based throttle for confirmation emails incorrectly checks the password reset path instead of the confirmation path, effectively disabling per-email limits for confirmation requests. This allows attackers to bypass rate limits by rotating IP addresses and send unlimited confirmation emails to any email address, as only a weak IP-based throttle (25 requests per 5 minutes) remains active. The vulnerability enables denial-of-service attacks that can overwhelm mail queues and facilitate user harassment through confirmation email spam. This is fixed in versions 4.2.24, 4.3.11 and 4.4.3.

## References
- https://github.com/mastodon/mastodon/commit/e2592419d93fb41be03c2f3ff6a122fecb0e0952
- https://github.com/mastodon/mastodon/releases/tag/v4.4.3
- https://github.com/mastodon/mastodon/security/advisories/GHSA-84ch-6436-c7mg
- https://nvd.nist.gov/vuln/detail/CVE-2025-54879
