# [H] Discourse allows permalinks to restricted resources to leak resource slugs to unauthorized users

## Summary
Severity: High
Advisory: BIT-discourse-2026-23743
Aliases: CVE-2026-23743, GHSA-v5jw-rxc6-4cvv
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-discourse-2026-23743
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2025.12.0 <2026.2.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, permalinks pointing to access-restricted resources (private topics, categories, posts, or hidden tags) were redirecting users to URLs containing the resource slug, even when the user didn't have access to view the resource. This leaked potentially sensitive information (e.g., private topic titles) via the redirect Location header and the 404 page's search box. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-v5jw-rxc6-4cvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-23743
