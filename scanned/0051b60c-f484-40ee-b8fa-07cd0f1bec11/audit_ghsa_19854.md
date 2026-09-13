# [M] Mattermost allows members with permission to convert public channels to private and convert private to public

## Summary
Severity: Medium
Advisory: GHSA-h5v9-xw2g-7hrq
CVE: CVE-2025-27933
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-h5v9-xw2g-7hrq
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0 <10.4.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0 <10.3.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0 <9.11.9
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <9.11.9
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250218135018-e644e3c8e393

## Details
Mattermost versions 10.4.x <= 10.4.2, 10.3.x <= 10.3.3, 9.11.x <= 9.11.8 fail to to enforce channel conversion restrictions, which allows members with permission to convert public channels to private ones to also convert private ones to public.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27933
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
