# [M] Discourse: Hidden first-post excerpt is emitted in Q&A schema JSON-LD

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-53960
Aliases: CVE-2026-53960, GHSA-j5j7-w5g3-43q8
Ecosystem: Bitnami
Published: 2026-08-21
Source: https://osv.dev/vulnerability/BIT-discourse-2026-53960
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.6.0 <2026.6.1

## Details
Discourse is an open-source discussion platform. Prior to 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0, hidden or otherwise unviewable first-post content was leaked as an excerpt in the publicly-served Q&A (QAPage) JSON-LD structured data, exposing it to any unauthenticated visitor and to search-engine crawlers. This issue is fixed in versions 2026.1.6, 2026.5.2, 2026.6.1, and 2026.7.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-j5j7-w5g3-43q8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53960
