# [M] Mastodon has a denial of service for quote authorization

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-33869
Aliases: CVE-2026-33869, GHSA-q4g8-82c5-9h33
Ecosystem: Bitnami
Published: 2026-03-31
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-33869
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.8

## Details
Mastodon is a free, open-source social network server based on ActivityPub. In versions on the 4.5.x branch prior to 4.5.8 and on the 4.4.x branch prior to 4.4.15, an attacker that knows of a quote before it has reached a server can prevent it from being correctly processed on that server. The vulnerability has been patched in Mastodon 4.5.8 and 4.4.15. Mastodon 4.3 and earlier are not affected because they do not support quotes.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-q4g8-82c5-9h33
- https://nvd.nist.gov/vuln/detail/CVE-2026-33869
