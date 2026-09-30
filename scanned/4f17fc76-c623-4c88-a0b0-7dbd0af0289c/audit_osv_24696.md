# [M] IDOR Vulnerability in Nextcloud Mail

## Summary
Severity: Medium
Advisory: CVE-2023-25160
Aliases: GHSA-m45f-r5gh-h6cx
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2023-02-13
Source: https://osv.dev/vulnerability/CVE-2023-25160
Type: osv

## Details
Nextcloud Mail is an email app for the Nextcloud home server platform. Prior to versions 2.2.1, 1.14.5, 1.12.9, and 1.11.8, an attacker can access the mail box by ID getting the subjects and the first characters of the emails. Users should upgrade to Mail 2.2.1 for Nextcloud 25, Mail 1.14.5 for Nextcloud 22-24, Mail 1.12.9 for Nextcloud 21, or Mail 1.11.8 for Nextcloud 20 to receive a patch. No known workarounds are available.

## References
- https://hackerone.com/reports/1784681
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25160.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-m45f-r5gh-h6cx
- https://nvd.nist.gov/vuln/detail/CVE-2023-25160
- https://github.com/nextcloud/mail/pull/7740
