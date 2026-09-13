# [H] Mastodon's blind LDAP injection in login allows the attacker to leak arbitrary attributes from LDAP database

## Summary
Severity: High
Advisory: BIT-mastodon-2023-28853
Aliases: CVE-2023-28853, GHSA-38g9-pfm9-gfqv
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-28853
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.1.0 <4.1.2

## Details
Mastodon is a free, open-source social network server based on ActivityPub Mastodon allows configuration of LDAP for authentication. Starting in version 2.5.0 and prior to versions 3.5.8, 4.0.4, and 4.1.2, the LDAP query made during login is insecure and the attacker can perform LDAP injection attack to leak arbitrary attributes from LDAP database. This issue is fixed in versions 3.5.8, 4.0.4, and 4.1.2.

## References
- http://www.openwall.com/lists/oss-security/2023/07/06/6
- https://github.com/mastodon/mastodon/blob/94cbd808b5b3e7999c7e77dc724b7e8c9dd2bdec/app/models/concerns/ldap_authenticable.rb#L7-L14
- https://github.com/mastodon/mastodon/blob/94cbd808b5b3e7999c7e77dc724b7e8c9dd2bdec/config/initializers/devise.rb#L398-L414
- https://github.com/mastodon/mastodon/pull/24379
- https://github.com/mastodon/mastodon/releases/tag/v3.5.8
- https://github.com/mastodon/mastodon/releases/tag/v4.0.4
- https://github.com/mastodon/mastodon/releases/tag/v4.1.2
- https://github.com/mastodon/mastodon/security/advisories/GHSA-38g9-pfm9-gfqv
- https://nvd.nist.gov/vuln/detail/CVE-2023-28853
