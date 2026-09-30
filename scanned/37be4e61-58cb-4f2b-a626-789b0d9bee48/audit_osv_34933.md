# [M] Nextcloud Calendar attachments of local files are offered to downloaded

## Summary
Severity: Medium
Advisory: CVE-2025-66550
Aliases: GHSA-f29c-ppmv-8mcv
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66550
Type: osv

## Details
Nextcloud Calendar is a calendar app for Nextcloud. Prior to 4.7.17 and 5.2.4, when a malicious user creates a calendar event with a crafted attachment that links to a download link of a file on the same Nextcloud server, the file would be downloaded without the user confirming the action. This vulnerability is fixed in 4.7.17 and 5.2.4.

## References
- https://hackerone.com/reports/3112033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66550.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-f29c-ppmv-8mcv
- https://nvd.nist.gov/vuln/detail/CVE-2025-66550
- https://github.com/nextcloud/calendar/commit/63a6c398db01391eb9fd5297a0d4c3d6e614f769
- https://github.com/nextcloud/calendar/pull/6971
