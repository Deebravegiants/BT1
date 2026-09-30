# [C] BIT-mastodon-2022-24307

## Summary
Severity: Critical
Advisory: BIT-mastodon-2022-24307
Aliases: CVE-2022-24307
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2022-24307
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=3.4.0 <3.4.6

## Details
Mastodon before 3.3.2 and 3.4.x before 3.4.6 has incorrect access control because it does not compact incoming signed JSON-LD activities. (JSON-LD signing has been supported since version 1.6.0.)

## References
- https://github.com/mastodon/mastodon/releases/tag/v3.3.2
- https://github.com/mastodon/mastodon/releases/tag/v3.4.6
- https://nvd.nist.gov/vuln/detail/CVE-2022-24307
