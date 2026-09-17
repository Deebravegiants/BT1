# [M] Discourse fixes loose hostname matching in spam host allowlist

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33393
Aliases: CVE-2026-33393, GHSA-95r5-p6qr-hgw6
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33393
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, the `allowed_spam_host_domains` check used `String#end_with?` without domain boundary validation, allowing domains like `attacker-example.com` to bypass spam protection when `example.com` was allowlisted. Versions 2026.3.0, 2026.2.1, and 2026.1.2 require exact match or proper subdomain match (preceded by `.`) to prevent suffix-based bypass of `newuser_spam_host_threshold`. No known workarounds are available.

## References
- https://github.com/discourse/discourse/commit/80b19c15fe9c7bc890d1a54f454c8446312ac6d2
- https://github.com/discourse/discourse/commit/d8467b9fbb3d9ed6047b4e508d3fef88a37b8a02
- https://github.com/discourse/discourse/commit/f99099cfbc6b76fe39d6fa2daa48efd69497fb8e
- https://github.com/discourse/discourse/security/advisories/GHSA-95r5-p6qr-hgw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33393
