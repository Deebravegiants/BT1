# [M] Mattermost Server does not safeguard against phishing via error page links

## Summary
Severity: Medium
Advisory: GHSA-vrh2-rprg-rgc6
CVE: CVE-2017-18891
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vrh2-rprg-rgc6
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=0 <4.0.5
- Go: `github.com/mattermost/mattermost-server` — affected >=4.1.0 <4.1.1
- Go: `github.com/mattermost/mattermost-server` — affected >=4.2.0-rc1 <4.2.0

## Details
An issue was discovered in Mattermost Server before 4.2.0, 4.1.1, and 4.0.5. It allows Phishing because an error page can have a link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18891
- https://github.com/mattermost/mattermost/pull/7378
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
