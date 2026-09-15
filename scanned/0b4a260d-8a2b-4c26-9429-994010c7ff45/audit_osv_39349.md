# [M] Nextcloud: Logged-in user bypasses share password and download restrictions on Text attachments via documentId leads to unauthorized file access

## Summary
Severity: Medium
Advisory: CVE-2026-45282
Aliases: GHSA-35fx-69q6-xpjr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45282
Type: osv

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 32.0.0 to before 32.0.9, and 33.0.0 to before 33.0.3, an authenticated attacker can access attachments of link shares when knowing the share token, circumventing password protection or download restrictions. It is applicable to any file that is shared directly, as the attacker only needs to know a documentId they own, apart of the mentioned share token. For shared folders the attacker has to know or guess a documentId of a file that is included inside the folder, making it much harder to exploit. The attacker can only extract an attachments, but not the file shared file or folder itself. It is recommended that the Nextcloud Server is upgraded to 33.0.3 or 32.0.9. It is recommended that the Nextcloud Enterprise Server is upgraded to 33.0.3, 32.0.9, 31.0.14.5, 30.0.17.9, 29.0.16.16, 28.0.14.17 or 27.1.11.5

## References
- https://hackerone.com/reports/3577244
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45282.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-35fx-69q6-xpjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45282
- https://github.com/nextcloud/text/pull/8499
