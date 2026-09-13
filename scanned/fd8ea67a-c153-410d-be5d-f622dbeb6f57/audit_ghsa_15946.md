# [M] Mattermost server allows authenticated user to delete arbitrary post

## Summary
Severity: Medium
Advisory: GHSA-g376-m3h3-mj4r
CVE: CVE-2024-50052
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-g376-m3h3-mj4r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240926115259-20ed58906adc

## Details
Mattermost versions 9.10.x <= 9.10.2, 9.11.x <= 9.11.1, 9.5.x <= 9.5.9 fail to check that the origin of the message in an integration action matches with the original post metadata which allows an authenticated user to delete an arbitrary post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50052
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
