# [M] Mastodon's verified profile links can be formatted in a misleading way

## Summary
Severity: Medium
Advisory: BIT-mastodon-2023-36462
Aliases: CVE-2023-36462, GHSA-55j9-c3mp-6fcq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-36462
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.1.0 <4.1.3

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Starting in version 2.6.0 and prior to versions 3.5.9, 4.0.5, and 4.1.3, an attacker can craft a verified profile link using specific formatting to conceal arbitrary parts of the link, enabling it to appear to link to a different URL altogether. The link is visually misleading, but clicking on it will reveal the actual link. This can still be used for phishing, though, similar to IDN homograph attacks. Versions 3.5.9, 4.0.5, and 4.1.3 contain a patch for this issue.

## References
- https://github.com/mastodon/mastodon/commit/610731b03dfcadd887078cb0399f4e514aa1931c
- https://github.com/mastodon/mastodon/releases/tag/v3.5.9
- https://github.com/mastodon/mastodon/releases/tag/v4.0.5
- https://github.com/mastodon/mastodon/releases/tag/v4.1.3
- https://github.com/mastodon/mastodon/security/advisories/GHSA-55j9-c3mp-6fcq
- https://nvd.nist.gov/vuln/detail/CVE-2023-36462
