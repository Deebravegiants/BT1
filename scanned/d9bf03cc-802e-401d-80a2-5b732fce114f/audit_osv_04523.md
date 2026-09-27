# [M] Discourse: Authorization bypass in oneboxer via user-controlled category id

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-32951
Aliases: CVE-2026-32951, GHSA-v93g-8f4f-4rgm
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-32951
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, an authenticated user can obtain shared draft topic titles by sending an inline onebox request with a category_id parameter matching the shared drafts category. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/0b4e6ff170362823d1cfe2a1a096785d0d77ee83
- https://github.com/discourse/discourse/security/advisories/GHSA-v93g-8f4f-4rgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32951
