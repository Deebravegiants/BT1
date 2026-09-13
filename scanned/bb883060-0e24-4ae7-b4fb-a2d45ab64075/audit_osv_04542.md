# [M] Discourse: Information Disclosure in Form Template API Due to Missing Authorization

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33514
Aliases: CVE-2026-33514, GHSA-w6g7-p2p9-2m5h
Ecosystem: Bitnami
Published: 2026-05-25
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33514
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. In versions prior to 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0, an authenticated user on a Discourse instance with the form templates feature enabled can read the name and structured content of form templates that are intended exclusively for categories they are not authorized to access. Impact is limited to disclosure of site configuration metadata. This issue has been fixed in versions 2026.1.4, 2026.3.1, 2026.4.1 and 2026.5.0.

## References
- https://github.com/discourse/discourse/commit/ae5c9570fb918442c4d96abc83c1e7e169909b02
- https://github.com/discourse/discourse/security/advisories/GHSA-w6g7-p2p9-2m5h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33514
