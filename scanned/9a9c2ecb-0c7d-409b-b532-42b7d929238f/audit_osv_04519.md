# [M] Discourse: Category group moderators can perform actions on topics in restricted categories without read access

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32615
Aliases: CVE-2026-32615, GHSA-pr9m-5hpq-wc57
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32615
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, category group moderators could perform privileged actions on topics inside private categories they did not have read access to. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/5a00b47523ec70cbb6e8efc3ac7677cc0a91448b
- https://github.com/discourse/discourse/security/advisories/GHSA-pr9m-5hpq-wc57
- https://nvd.nist.gov/vuln/detail/CVE-2026-32615
