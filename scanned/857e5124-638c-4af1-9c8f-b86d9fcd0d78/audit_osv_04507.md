# [M] Discourse has Unauthorized Post Data Exposure in discourse-user-notes

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-30889
Aliases: CVE-2026-30889, GHSA-5qm9-r98f-g4mq
Ecosystem: Bitnami
Published: 2026-03-27
Source: https://osv.dev/vulnerability/BIT-discourse-2026-30889
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.3.0 <2026.3.0

## Details
Discourse is an open-source discussion platform. Prior to versions 2026.3.0, 2026.2.1, and 2026.1.2, a moderator could exploit insufficient authorization checks to access metadata of posts they should not have permission to view. Versions 2026.3.0, 2026.2.1, and 2026.1.2 contain a patch.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-5qm9-r98f-g4mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-30889
