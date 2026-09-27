# [M] Discourse: Hidden post revisions leak through adjacent visible diffs

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-59828
Aliases: CVE-2026-59828, GHSA-q456-4f8q-42vx
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-discourse-2026-59828
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.7.0

## Details
Discourse is an open-source discussion platform. Prior to 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5, post revisions that should be hidden from regular users could be leaked through visible diffs on adjacent revisions serialized by PostRevisionSerializer. This issue is fixed in versions 2026.6.0, 2026.5.1, 2026.4.2, and 2026.1.5.

## References
- https://github.com/discourse/discourse/commit/1f26c1163ce87a2abbd1d01780ab1b5fb16e75f6
- https://github.com/discourse/discourse/commit/8b773332b0f937dfcd894ed56d56fc5a81578d9d
- https://github.com/discourse/discourse/commit/8d36da1b68c906592abde3f2e94d505cdf097435
- https://github.com/discourse/discourse/commit/d58988d46bb1019bfa8b8330ae81a1a134e08511
- https://github.com/discourse/discourse/releases/tag/v2026.1.5
- https://github.com/discourse/discourse/releases/tag/v2026.4.2
- https://github.com/discourse/discourse/releases/tag/v2026.5.1
- https://github.com/discourse/discourse/releases/tag/v2026.6.0
- https://github.com/discourse/discourse/security/advisories/GHSA-q456-4f8q-42vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-59828
