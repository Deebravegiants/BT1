# [M] Mastodon's signature-dependent ActivityPub collection responses cached under signature-independent keys (Web Cache Poisoning via `Rails.cache`)

## Summary
Severity: Medium
Advisory: BIT-mastodon-2026-25540
Aliases: CVE-2026-25540, GHSA-ccpr-m53r-mfwr
Ecosystem: Bitnami
Published: 2026-02-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-25540
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=0 <4.5.6

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to versions 4.3.19, 4.4.13, 4.5.6, Mastodon is vulnerable to web cache poisoning via `Rails.cache. When AUTHORIZED_FETCH is enabled, the ActivityPub endpoints for pinned posts and featured hashtags have contents that depend on the account that signed the HTTP request. However, these contents are stored in an internal cache and reused with no regards to the signing actor. As a result, an empty response generated for a blocked user account may be served to requests from legitimate non-blocked actors, or conversely, content intended for non-blocked actors may be returned to blocked actors. This issue has been patched in versions 4.3.19, 4.4.13, 4.5.6.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-ccpr-m53r-mfwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25540
