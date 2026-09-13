# [M] Mastodon may allow a remote suspension bypass

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-23961
Aliases: CVE-2026-23961, GHSA-5h2f-wg8j-xqwp
Ecosystem: Bitnami
Published: 2026-02-03
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-23961
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.5

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Mastodon allows server administrators to suspend remote users to prevent interactions. However, some logic errors allow already-known posts from such suspended users to appear in timelines if boosted. Furthermore, under certain circumstances, previously-unknown posts from suspended users can be processed. This issue allows old posts from suspended users to occasionally end up on timelines on all Mastodon versions. Additionally, on Mastodon versions from v4.5.0 to v4.5.4, v4.4.5 to v4.4.11, v4.3.13 to v4.3.17, and v4.2.26 to v4.2.29, remote suspended users can partially bypass the suspension to get new posts in. Mastodon versions v4.5.5, v4.4.12, v4.3.18 are patched.

## References
- https://github.com/mastodon/mastodon/releases/tag/v4.3.18
- https://github.com/mastodon/mastodon/releases/tag/v4.4.12
- https://github.com/mastodon/mastodon/releases/tag/v4.5.5
- https://github.com/mastodon/mastodon/security/advisories/GHSA-5h2f-wg8j-xqwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-23961
