# [M] Mattermost fails to restrict channel export of archived channels

## Summary
Severity: Medium
Advisory: GHSA-q8p2-2hwc-jw64
CVE: CVE-2025-24526
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-q8p2-2hwc-jw64
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250110161910-96195f1bd746
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0-rc1 <9.11.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0-rc1 <10.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0-rc1 <10.3.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0-rc1 <10.4.2

## Details
Mattermost versions 10.1.x <= 10.1.3, 10.4.x <= 10.4.1, 9.11.x <= 9.11.7, 10.3.x <= 10.3.2, 10.2.x <= 10.2.2 fail to restrict channel export of archived channels when the "Allow users to view archived channels" is disabled which allows a user to export channel contents when they shouldn't have access to it

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24526
- https://github.com/mattermost/mattermost-plugin-channel-export/issues/51
- https://github.com/mattermost/mattermost-plugin-channel-export/commit/3c052b66207fb734bfc4c948941e7f7522a82550
- https://github.com/mattermost/mattermost/commit/96195f1bd7467f572525c35b5087acaeb53daa63
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
