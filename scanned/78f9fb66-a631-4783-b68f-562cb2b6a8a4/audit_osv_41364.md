# [H] Hoppscotch: Admin RCE via MAILER_SMTP_URL nodemailer sendmail-transport injection

## Summary
Severity: High
Advisory: CVE-2026-59721
Aliases: GHSA-v7q6-r45w-2c6r
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59721
Type: osv

## Details
Hoppscotch is an open source API development ecosystem. Prior to 2026.6.0, the updateInfraConfigs GraphQL mutation in admin/infra.resolver.ts accepts an attacker-controlled MAILER_SMTP_URL value, and validateSMTPUrl in utils.ts permits path, query, or fragment content that nodemailer parses into sendmail transport options, allowing an admin to execute arbitrary commands as root in the backend container after restart and mail sending. This issue is fixed in version 2026.6.0.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59721.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-v7q6-r45w-2c6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-59721
- https://github.com/hoppscotch/hoppscotch/commit/73a88c82b1b2cada26cc4b2bc095b54554242239
- https://github.com/hoppscotch/hoppscotch/pull/6413
