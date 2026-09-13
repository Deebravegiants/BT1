# [M] Discourse: Hidden group names and access metadata are exposed to moderators through the `category-chatables` endpoint

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33300
Aliases: CVE-2026-33300, GHSA-wrwm-vqx2-6x4v
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33300
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, an authorization bypass in the Category Chatables Controller show action allowed moderators to get information on hidden groups names and user count. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/07f66658cce81a099a0d7115db5f3c69f5d3cca2
- https://github.com/discourse/discourse/security/advisories/GHSA-wrwm-vqx2-6x4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33300
