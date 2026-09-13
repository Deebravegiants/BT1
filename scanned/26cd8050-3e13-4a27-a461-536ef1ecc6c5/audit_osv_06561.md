# [H] Mastodon Invalid Domain Name Normalization vulnerability

## Summary
Severity: High
Advisory: BIT-mastodon-2023-42451
Aliases: CVE-2023-42451, GHSA-v3xf-c9qf-j667
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-42451
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.1.0 <4.1.8

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to versions 3.5.14, 4.0.10, 4.1.8, and 4.2.0, under certain circumstances, attackers can exploit a flaw in domain name normalization to spoof domains they do not own. Versions 3.5.14, 4.0.10, 4.1.8, and 4.2.0 contain a patch for this issue.

## References
- https://github.com/mastodon/mastodon/commit/eeab3560fc0516070b3fb97e089b15ecab1938c8
- https://github.com/mastodon/mastodon/security/advisories/GHSA-v3xf-c9qf-j667
- https://nvd.nist.gov/vuln/detail/CVE-2023-42451
