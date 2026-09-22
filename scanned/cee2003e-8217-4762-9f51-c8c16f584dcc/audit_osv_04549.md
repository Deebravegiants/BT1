# [M] Discourse: Non-staff group owners can see email password in plaintext through group history

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-44784
Aliases: CVE-2026-44784, GHSA-94c5-j24g-r99f
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-discourse-2026-44784
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.4.0 <2026.4.1

## Details
Discourse is an open-source discussion platform. From versions 2026.1.0 to before 2026.1.4, 2026.3.0 to before 2026.3.1, and 2026.4.0 to before 2026.4.1, group owners who are not necessarily admins or moderators can view a group's outgoing email/SMTP credentials in plaintext via the group history log (/groups/:name/logs.json). Affected fields: email_password, email_username, smtp_server, smtp_port, smtp_ssl_mode. The most sensitive item is the SMTP password, which an owner could use to send mail as the group from outside Discourse. This impacts sites that have configured per-group SMTP credentials and granted group ownership to users who should not have access to those credentials. This issue has been patched in versions 2026.1.4, 2026.3.1, 2026.4.1, and 2026.5.0.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-94c5-j24g-r99f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44784
