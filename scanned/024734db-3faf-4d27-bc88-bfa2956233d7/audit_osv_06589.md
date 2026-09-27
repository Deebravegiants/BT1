# [M] Mastodon: Spoofing of attribution domains

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-50128
Aliases: CVE-2026-50128
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-50128
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.11

## Details
Mastodon is a free, open-source social network server based on ActivityPub. From 4.3.0 until 4.5.11 and 4.4.18, Mastodon has a feature to let websites credit authors of their articles. To prevent false attribution claims, Mastodon uses the attributionDomains JSON-LD term, however, an error in how it is defined makes Linked Data Signatures on the toot:attributionDomains property ineffective. An attacker can arbitrarily modify the attributionDomains value of a legitimately signed Update activity and bypass Mastodon’s signature verification. This vulnerability is fixed in 4.5.11 and 4.4.18.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-pwx3-qcgw-vh7h
- https://github.com/mastodon/mastodon/security/advisories/GHSA-rwcw-vq68-g34p
- https://nvd.nist.gov/vuln/detail/CVE-2026-50128
