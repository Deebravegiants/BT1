# [H] Mastodon: Persistent anonymous DoS via unhandled NoMethodError in MATH_TRANSFORMER

## Summary
Severity: High
Advisory: BIT-mastodon-2026-50129
Aliases: CVE-2026-50129, GHSA-qrgq-9fx2-vf2r
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-50129
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.11

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to 4.5.11, 4.4.18, and 4.3.24, a DoS can be triggered by (Uncaught Exception vulerability), due to missing exception handling in the math sanitizer. Malformed <math> nodes can result in a DoS of a whole server or targeted users services, depending on the type of action that includes the malformed nodes and the services interacting with it. This vulnerability is fixed in 4.5.11, 4.4.18, and 4.3.24.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-qrgq-9fx2-vf2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-50129
