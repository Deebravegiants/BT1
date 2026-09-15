# [M] Improper Access Control in Mattermost Google Drive Plugin File Creation Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-2299
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-2299
Type: osv

## Details
The Mattermost Google Drive plugin before version 1.1.0 fails to validate channel membership in the file creation endpoint, allowing authenticated users with a connected Google account to share Google Drive files to unauthorized private channels and disclose private channel membership.

## References
- https://github.com/mattermost/mattermost-plugin-google-drive/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2299.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2299
- https://github.com/mattermost/mattermost-plugin-google-drive
