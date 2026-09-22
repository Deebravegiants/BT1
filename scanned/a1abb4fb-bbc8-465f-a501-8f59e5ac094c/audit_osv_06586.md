# [H] Mastodon: SSRF Bypass via IPv6 Unspecified Address (::)

## Summary
Severity: High
Advisory: BIT-mastodon-2026-46348
Aliases: CVE-2026-46348, GHSA-crr4-7rm4-8gpw
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-mastodon-2026-46348
Type: osv

## Affected
- Bitnami: `mastodon` — affected >=4.5.0 <4.5.10

## Details
Mastodon is a free, open-source social network server based on ActivityPub. Prior to 4.5.10, 4.4.17, and 4.3.23, the list of disallowed IP address ranges was lacking an IP address range that can be used to reach local IP addresses. An attacker can use an IP address in the affected range to make Mastodon perform HTTP requests against loopback interfaces, potentially allowing access to otherwise private resources and services. This vulnerability is fixed in 4.5.10, 4.4.17, and 4.3.23.

## References
- https://github.com/mastodon/mastodon/security/advisories/GHSA-crr4-7rm4-8gpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-46348
