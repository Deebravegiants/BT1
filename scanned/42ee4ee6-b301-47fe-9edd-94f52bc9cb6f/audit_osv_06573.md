# [M] Mastodon quotes control can be bypassed

## Summary
Severity: Medium
Advisory: BIT-mastodon-2025-62605
Aliases: CVE-2025-62605, GHSA-8h43-rcqj-wpc6
Ecosystem: Bitnami
Published: 2025-10-23
Source: https://osv.dev/vulnerability/BIT-mastodon-2025-62605
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.4.0 <4.4.8

## Details
Mastodon is a free, open-source social network server based on ActivityPub. In Mastodon version 4.4, support for verifiable quote posts with quote controls was added, but it is possible for an attacker to bypass these controls in Mastodon versions prior to 4.4.8 and 4.5.0. Mastodon internally treats reblogs as statuses. Since they were not special-treated, an attacker could reblog any post, then quote their reblog, technically quoting themselves, but having the quote feature a preview of the post they did not get authorization for with all of the affordances that would be otherwise denied by the quote controls. This issue has been patched in versions 4.4.8 and 4.5.0.

## References
- https://github.com/mastodon/mastodon/commit/2dc4552229b55e2e4adaef675e68ed7ae123d78e
- https://github.com/mastodon/mastodon/commit/405a49df44033e7d179f3d44d59fb68a67d54789
- https://github.com/mastodon/mastodon/releases/tag/v4.4.8
- https://github.com/mastodon/mastodon/releases/tag/v4.5.0-beta.2
- https://github.com/mastodon/mastodon/security/advisories/GHSA-8h43-rcqj-wpc6
- https://nvd.nist.gov/vuln/detail/CVE-2025-62605
