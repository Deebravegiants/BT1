# [M] Nextcloud Calendar's event create can create attachments that link to other websites

## Summary
Severity: Medium
Advisory: CVE-2024-37316
Aliases: GHSA-2r7q-vfmv-79qf
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2024-06-14
Source: https://osv.dev/vulnerability/CVE-2024-37316
Type: osv

## Details
Nextcloud Calendar is a calendar app for Nextcloud. Authenticated users could create an event with manipulated attachment data leading to a bad redirect for participants when clicked. It is recommended that the Nextcloud Calendar App is upgraded to 4.6.8 or 4.7.2.

## References
- https://hackerone.com/reports/2457588
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37316.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2r7q-vfmv-79qf
- https://nvd.nist.gov/vuln/detail/CVE-2024-37316
- https://github.com/nextcloud/calendar/pull/5966
