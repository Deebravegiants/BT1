# [H] Mastodon vulnerable to Denial of Service from a single post (client/server)

## Summary
Severity: High
Advisory: BIT-mastodon-2026-23962
Aliases: CVE-2026-23962, GHSA-gg8q-rcg7-p79g
Ecosystem: Bitnami
Published: 2026-02-03
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-23962
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.5

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Mastodon versions before v4.3.18, v4.4.12, and v4.5.5 do not have a limit on the maximum number of poll options for remote posts, allowing attackers to create polls with a very large amount of options, greatly increasing resource consumption. Depending on the number of poll options, an attacker can cause disproportionate resource usage in both Mastodon servers and clients, potentially causing Denial of Service either server-side or client-side. Mastodon versions v4.5.5, v4.4.12, v4.3.18 are patched.

## References
- https://github.com/mastodon/mastodon/releases/tag/v4.3.18
- https://github.com/mastodon/mastodon/releases/tag/v4.4.12
- https://github.com/mastodon/mastodon/releases/tag/v4.5.5
- https://github.com/mastodon/mastodon/security/advisories/GHSA-gg8q-rcg7-p79g
- https://nvd.nist.gov/vuln/detail/CVE-2026-23962
