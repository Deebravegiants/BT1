# [H] Mastodon has SSRF Protection bypass

## Summary
Severity: High
Advisory: BIT-mastodon-2026-22245
Aliases: CVE-2026-22245, GHSA-xfrj-c749-jxxq
Ecosystem: Bitnami
Published: 2026-01-13
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-22245
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.4

## Details
Mastodon is a free, open-source social network server based on ActivityPub. By nature, Mastodon performs a lot of outbound requests to user-provided domains. Mastodon, however, has some protection mechanism to disallow requests to local IP addresses (unless specified in `ALLOWED_PRIVATE_ADDRESSES`) to avoid the "confused deputy" problem. The list of disallowed IP address ranges was lacking some IP address ranges that can be used to reach local IP addresses. An attacker can use an IP address in the affected ranges to make Mastodon perform HTTP requests against loopback or local network hosts, potentially allowing access to otherwise private resources and services. This is fixed in Mastodon v4.5.4, v4.4.11, v4.3.17 and v4.2.29.

## References
- https://github.com/mastodon/mastodon/commit/0f4e8a6240b5af1f2c3f34d2793d8610c6ef2aca
- https://github.com/mastodon/mastodon/commit/17022907866710a72a1b1fc0a5ce9538bad1b4c3
- https://github.com/mastodon/mastodon/commit/71ae4cf2cf5138ccdda64b1b1d665849b688686d
- https://github.com/mastodon/mastodon/security/advisories/GHSA-xfrj-c749-jxxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-22245
