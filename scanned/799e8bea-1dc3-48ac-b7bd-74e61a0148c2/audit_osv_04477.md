# [M] Discourse non-admin moderators can exfiltrate private content via post ownership transfer

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-68933
Aliases: CVE-2025-68933, GHSA-hpxv-mw7v-fqg2
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-68933
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, non-admin moderators with the `moderators_change_post_ownership` setting enabled can change ownership of posts in private messages and restricted categories they cannot access, then export their data to view the content. This is a broken access control vulnerability affecting sites that grant moderators post ownership transfer permissions. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. The patch adds visibility checks for both the topic and posts before allowing ownership transfer. As a workaround, disable the `moderators_change_post_ownership` site setting to prevent non-admin moderators from using the post ownership transfer feature.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-hpxv-mw7v-fqg2
- https://nvd.nist.gov/vuln/detail/CVE-2025-68933
