# [M] Discourse: Shared-draft titles and excerpts leak through group post serialization

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-55704
Aliases: CVE-2026-55704, GHSA-fxw4-38v9-76v8
Ecosystem: Bitnami
Published: 2026-08-21
Source: https://osv.dev/vulnerability/BIT-discourse-2026-55704
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior o 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, users who were allowed to view a group’s activity, but were not permitted to see shared drafts, could still receive shared-draft entries through the group posts and group mentions endpoints. This could disclose shared-draft topic titles and post excerpt/content, resulting in an information disclosure of unpublished draft material. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-fxw4-38v9-76v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-55704
