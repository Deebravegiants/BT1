# [M] Discourse has insecure default configuration that allows non-admin moderators to takeover any non-staff account via email change

## Summary
Severity: Medium
Advisory: BIT-discourse-2025-69289
Aliases: CVE-2025-69289, GHSA-p39j-x54c-rwqq
Ecosystem: Bitnami
Published: 2026-02-02
Source: https://osv.dev/vulnerability/BIT-discourse-2025-69289
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.0

## Details
Discourse is an open source discussion platform. A privilege escalation vulnerability in versions prior to 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0 allows a non-admin moderator to bypass email-change restrictions, allowing a takeover of non-staff accounts. This issue is patched in versions 3.5.4, 2025.11.2, 2025.12.1, and 2026.1.0. As a workaround, ensure moderators are trusted or enable the "require_change_email_confirmation" setting.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-p39j-x54c-rwqq
- https://nvd.nist.gov/vuln/detail/CVE-2025-69289
