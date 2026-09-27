# [C] Mastodon Remote user impersonation and takeover

## Summary
Severity: Critical
Advisory: BIT-mastodon-2024-23832
Aliases: CVE-2024-23832, GHSA-3fjr-858r-92rw
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2024-23832
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.2.0 <4.2.5

## Details
Mastodon is a free, open-source social network server based on ActivityPub Mastodon allows configuration of LDAP for authentication. Due to insufficient origin validation in all Mastodon, attackers can impersonate and take over any remote account. Every Mastodon version prior to 3.5.17 is vulnerable, as well as 4.0.x versions prior to 4.0.13, 4.1.x version prior to 4.1.13, and 4.2.x versions prior to 4.2.5.

## References
- http://www.openwall.com/lists/oss-security/2024/02/02/4
- https://github.com/mastodon/mastodon/commit/1726085db5cd73dd30953da858f9887bcc90b958
- https://github.com/mastodon/mastodon/security/advisories/GHSA-3fjr-858r-92rw
- https://nvd.nist.gov/vuln/detail/CVE-2024-23832
