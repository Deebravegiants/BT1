# [M] Mattermost doesn't validate decompressed archive entry sizes during file extraction

## Summary
Severity: Medium
Advisory: GHSA-vhgh-g7x8-4rx8
CVE: CVE-2026-3114
CWE: CWE-409
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-vhgh-g7x8-4rx8
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.1
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.3.0 <11.3.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.2.0 <11.2.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.12
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260105080200-d27a2195068d <8.0.0-20260217110922-b7d4a1f1f59b

## Details
Mattermost versions 11.4.x <= 11.4.0, 11.3.x <= 11.3.1, 11.2.x <= 11.2.3, 10.11.x <= 10.11.11 fail to validate decompressed archive entry sizes during file extraction which allows authenticated users with file upload permissions to cause a denial of service via crafted zip archives containing highly compressed entries (zip bombs) that exhaust server memory. Mattermost Advisory ID: MMSA-2026-00598.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3114
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
