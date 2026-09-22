# [M] DIscourse doesn't prevent whispers to leak in excerpts

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-27162
Aliases: CVE-2026-27162, GHSA-gffm-43j4-372w
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-27162
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, `posts_nearby` was checking topic access but then returning all posts regardless of type, including whispers that should only be visible to whisperers. Use `Post.secured(guardian)` to properly filter post types based on user permissions. Versions 2025.12.2, 2026.1.1, and 2026.2.0 patch the issue. No known workarounds are available.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-gffm-43j4-372w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27162
