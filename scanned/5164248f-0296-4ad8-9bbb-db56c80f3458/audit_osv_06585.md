# [H] Mastodon: Insufficient verification of email addresses

## Summary
Severity: High
Advisory: BIT-mastodon-2026-41259
Aliases: CVE-2026-41259, GHSA-5r37-qpwq-2jhh
Ecosystem: Bitnami
Published: 2026-04-27
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-41259
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.9

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to v4.5.9, v4.4.16, and v4.3.22, Mastodon allows restricting new user sign-up based on e-mail domain names, and performs basic validation on e-mail addresses, but fails to restrict characters that are interpreted differently by some mailing servers. This vulnerability is fixed in v4.5.9, v4.4.16, and v4.3.22.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-5r37-qpwq-2jhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-41259
