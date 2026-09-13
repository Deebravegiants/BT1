# [C] Mastodon vulnerable to arbitrary file creation through media attachments

## Summary
Severity: Critical
Advisory: BIT-mastodon-2023-36460
Aliases: CVE-2023-36460, GHSA-9928-3cp5-93fm
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2023-36460
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.1.0 <4.1.3

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Starting in version 3.5.0 and prior to versions 3.5.9, 4.0.5, and 4.1.3, attackers using carefully crafted media files can cause Mastodon's media processing code to create arbitrary files at any location. This allows attackers to create and overwrite any file Mastodon has access to, allowing Denial of Service and arbitrary Remote Code Execution. Versions 3.5.9, 4.0.5, and 4.1.3 contain a patch for this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/07/06/4
- https://github.com/mastodon/mastodon/commit/dc8f1fbd976ae544720a4e07120d9a91b2722440
- https://github.com/mastodon/mastodon/releases/tag/v3.5.9
- https://github.com/mastodon/mastodon/releases/tag/v4.0.5
- https://github.com/mastodon/mastodon/releases/tag/v4.1.3
- https://github.com/mastodon/mastodon/security/advisories/GHSA-9928-3cp5-93fm
- https://nvd.nist.gov/vuln/detail/CVE-2023-36460
