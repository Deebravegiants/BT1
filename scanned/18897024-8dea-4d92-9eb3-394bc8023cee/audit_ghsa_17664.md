# [C] Mattermost allows authenticated users to write files to arbitrary locations

## Summary
Severity: Critical
Advisory: GHSA-qh58-9v3j-wcjc
CVE: CVE-2025-4981
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-qh58-9v3j-wcjc
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <0.0.0-20250519205859-65aec10162f6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250519205859-65aec10162f6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.5.0 <10.5.6
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.16
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.8.0 <10.8.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.7.0 <10.7.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.6.0 <10.6.6

## Details
Mattermost versions 10.5.x <= 10.5.5, 9.11.x <= 9.11.15, 10.8.x <= 10.8.0, 10.7.x <= 10.7.2, 10.6.x <= 10.6.5 fail to sanitize filenames in the archive extractor which allows authenticated users to write files to arbitrary locations on the filesystem via uploading archives with path traversal sequences in filenames, potentially leading to remote code execution. The vulnerability impacts instances where file uploads and document search by content is enabled (FileSettings.EnableFileAttachments = true and FileSettings.ExtractContent = true). These configuration settings are enabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4981
- https://github.com/mattermost/mattermost/commit/65aec10162f612d98edf91cc66bf7e781868448b
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
