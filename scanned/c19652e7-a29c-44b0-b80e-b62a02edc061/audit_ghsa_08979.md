# [M] Mattermost allows authenticated users to gain access to private repositories

## Summary
Severity: Medium
Advisory: GHSA-r5vf-grcx-5vqp
CVE: CVE-2026-28735
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-r5vf-grcx-5vqp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15
- Go: `github.com/mattermost/mattermost-plugin-github` — affected >=0 <1.0.1-0.20260318132218-6e6b740c4852

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to validate the OAuth token scope on the callback which allows an authenticated Mattermost user to gain access to private repositories via modifying the scope parameter in the GitHub authorization URL. Mattermost Advisory ID: MMSA-2026-00628

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28735
- https://github.com/mattermost/mattermost-plugin-github/commit/6e6b740c4852cdfa136ee0ced160da832285c353
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
