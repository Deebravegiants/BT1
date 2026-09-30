# [M] Discourse: Improper Access Control in discourse-ai Allows Unauthorized Category Content Exposure

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-33415
Aliases: CVE-2026-33415, GHSA-vj5f-gg8m-93xg
Ecosystem: Bitnami
Published: 2026-04-07
Source: https://osv.dev/vulnerability/BIT-discourse-2026-33415
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.2.0 <2026.2.2

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.3, and 2026.2.0 to before 2026.2.2, an authenticated moderator-level user could retrieve post content, topic titles, and usernames from categories they were not authorized to view. Insufficient access controls on a sentiment analytics endpoint allowed category permission boundaries to be bypassed. This issue has been patched in versions 2026.1.3, 2026.2.2, and 2026.3.0.

## References
- https://github.com/discourse/discourse/commit/e1bb146a1fadc863a516fbc26c6277273a025308
- https://github.com/discourse/discourse/security/advisories/GHSA-vj5f-gg8m-93xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33415
