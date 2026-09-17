# [H] Discourse: Hidden tag names leaked via category serializers

## Summary
Severity: High
Advisory: BIT-discourse-2026-49256
Aliases: CVE-2026-49256, GHSA-mwp7-572g-6qpx
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-discourse-2026-49256
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.5.0 <2026.5.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, restricted tag and tag-group names attached to publicly readable categories as allowed_tags, allowed_tag_groups, or required tag groups could leak to anonymous and unauthorized users through category and group endpoints. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-mwp7-572g-6qpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-49256
