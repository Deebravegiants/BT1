# [M] Mattermost fails to validate team-specific upload_file permissions

## Summary
Severity: Medium
Advisory: GHSA-xpvf-6qcc-9jqc
CVE: CVE-2026-4265
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-xpvf-6qcc-9jqc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260107144005-c7f6efdfb035
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <5.3.2-0.20260107144005-c7f6efdfb035
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0-rc1 <10.11.11
- Go: `github.com/mattermost/mattermost-server` — affected >=11.2.0-rc1 <11.2.3
- Go: `github.com/mattermost/mattermost-server` — affected >=11.3.0-rc1 <11.3.1

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to validate team-specific upload_file permissions which allows a guest user to post files in channels where they lack upload_file permission via uploading files in a team where they have permission and reusing the file metadata in a POST request to a different team. Mattermost Advisory ID: MMSA-2025-00553

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4265
- https://github.com/mattermost/mattermost/commit/c7f6efdfb035490f494b3177996ee5f4b278c988
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
