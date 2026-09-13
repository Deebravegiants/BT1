# [M] Mattermost doesn't check public/private permissions

## Summary
Severity: Medium
Advisory: GHSA-m79q-8qf5-v622
CVE: CVE-2026-6343
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-m79q-8qf5-v622
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost-plugin-playbooks` — affected >=0 <1.41.1-0.20260309184833-887d9cacb616

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to check public/private permissions which allows members without these permissions to access public playbooks via /get.. Mattermost Advisory ID: MMSA-2026-00591

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6343
- https://github.com/mattermost/mattermost-plugin-playbooks/commit/887d9cacb61655d40f20ad9d6e35b408a127c380
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
