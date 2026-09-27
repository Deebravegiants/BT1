# [M] Discourse users archives leaked to users with moderation privileges

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-68666
Aliases: CVE-2025-68666, GHSA-xmvw-jjqq-25mv
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68666
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2025.12.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, users archives are viewable by users with moderation privileges even though moderators should not have access to the archives. Private topic/post content made by the users are leaked through the archives leading to a breach of confidentiality. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. To work around this problem, a site admin can temporarily revoke the moderation role from all moderators until the Discourse instance has been upgraded to a version that has been patched.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-xmvw-jjqq-25mv
- https://nvd.nist.gov/vuln/detail/CVE-2025-68666
