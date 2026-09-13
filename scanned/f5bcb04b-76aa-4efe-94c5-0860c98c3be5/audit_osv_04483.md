# [M] Discourse staff action logs expose sensitive information to moderators

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-24742
Aliases: CVE-2026-24742, GHSA-hwjv-9gqj-m7h6
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2026-24742
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. In versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0, non-admin moderators can view sensitive information in staff action logs that should be restricted to administrators only. The exposed information includes webhook payload URLs and secrets, API key details, site setting changes, private message content, restricted category names and structures, and private chat channel titles. This allows moderators to bypass intended access controls and extract confidential data by monitoring the staff action logs. With leaked webhook secrets, an attacker could potentially spoof webhook events to integrated services. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. As a workaround, site administrators should review and limit moderator appointments to fully trusted users. There is no configuration-based workaround to prevent this access.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-hwjv-9gqj-m7h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-24742
