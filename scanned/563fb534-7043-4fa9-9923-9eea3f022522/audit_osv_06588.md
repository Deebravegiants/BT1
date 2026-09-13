# [M] Mastodon: Removal of integrity-protected JSON entries from signed activities

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-48028
Aliases: CVE-2026-48028, GHSA-53m7-2wrh-q839
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-48028
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.10

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to 4.5.10, 4.4.17, and 4.3.23, Mastodon's normalization of incoming activities signed with Linked-Data Signatures does not sufficiently protect the activities from a certain class of spoofing, allowing threat actors to remove JSON entries from valid signed activities from a third-party actor. This vulnerability is fixed in 4.5.10, 4.4.17, and 4.3.23.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-53m7-2wrh-q839
- https://nvd.nist.gov/vuln/detail/CVE-2026-48028
