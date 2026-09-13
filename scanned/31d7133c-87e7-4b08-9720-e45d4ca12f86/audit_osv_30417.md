# [H] Nextcloud Mail auto configurator can be tricked into sending account information to wrong servers

## Summary
Severity: High
Advisory: CVE-2024-52508
Aliases: GHSA-vmhx-hwph-q6mc
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52508
Type: osv

## Details
Nextcloud Mail is the mail app for Nextcloud, a self-hosted productivity platform. When a user is trying to set up a mail account with an email address like user@example.tld that does not support auto configuration, and an attacker managed to register autoconfig.tld, the used email details would be send to the server of the attacker. It is recommended that the Nextcloud Mail app is upgraded to 1.14.6, 1.15.4, 2.2.11, 3.6.3, 3.7.7 or 4.0.0.

## References
- https://hackerone.com/reports/2508422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52508.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vmhx-hwph-q6mc
- https://nvd.nist.gov/vuln/detail/CVE-2024-52508
- https://github.com/nextcloud/mail/commit/a84c70e15d814dab6f0e8eda71bbaaf48152079b
- https://github.com/nextcloud/mail/pull/9964
