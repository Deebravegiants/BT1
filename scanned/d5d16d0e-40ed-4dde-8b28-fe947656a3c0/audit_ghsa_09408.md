# [M] Mattermost doesn't validate user-supplied input in API request handlers

## Summary
Severity: Medium
Advisory: GHSA-rmvv-8v8w-rf7x
CVE: CVE-2026-4646
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-rmvv-8v8w-rf7x
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15
- Go: `github.com/mattermost/mattermost-plugin-github` — affected >=0 <1.0.1-0.20260330164815-c2840e980b3c

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to validate user-supplied input in API request handlers which allows an authenticated attacker to crash the plugin process via a crafted HTTP request to the PR details endpoint. Mattermost Advisory ID: MMSA-2026-00638

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4646
- https://github.com/mattermost/mattermost-plugin-github/commit/c2840e980b3c2bd08db656eaa6a0fe26bcbf4695
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
