# [H] Mastodon: Unwanted deactivation of SSL/TLS certificate verification

## Summary
Severity: High
Advisory: BIT-mastodon-2026-59825
Aliases: CVE-2026-59825, GHSA-3rhr-8phh-jm86
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-59825
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.12

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to 4.4.19 and from 4.5.0 until 4.5.12, Mastodon's app/models/concerns/user/ldap_authenticable.rb mutates OpenSSL::SSL::SSLContext::DEFAULT_PARAMS when LDAP authentication uses LDAP_TLS_NO_VERIFY=true, disabling SSL and TLS certificate verification globally for requests made by puma web processes while sidekiq background jobs remain unaffected. This issue is fixed in versions 4.4.19 and 4.5.12.

## References
- https://github.com/mastodon/mastodon/commit/2ccb6ef277e725d1932295690cf8ab9d3dc03149
- https://github.com/mastodon/mastodon/commit/5748d0b16ea09001e0933f76c7afe814e09652ef
- https://github.com/mastodon/mastodon/commit/761c61b42590a2fd91442fc15a0a7583e48bbea4
- https://github.com/mastodon/mastodon/pull/39571
- https://github.com/mastodon/mastodon/releases/tag/v4.4.19
- https://github.com/mastodon/mastodon/releases/tag/v4.5.12
- https://github.com/mastodon/mastodon/security/advisories/GHSA-3rhr-8phh-jm86
- https://nvd.nist.gov/vuln/detail/CVE-2026-59825
