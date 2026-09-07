# [M] Mattermost has an Incorrect Authorization issue

## Summary
Severity: Medium
Advisory: GHSA-6cfr-wp44-6qmv
CVE: CVE-2026-4055
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-6cfr-wp44-6qmv
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=8.0.0-20260304132957-9f2616376582 <8.0.0-20260320113102-f2b3d1c6a945

## Details
Mattermost versions 11.5.x <= 11.5.1 fail to validate team-level run_create permission against the target team when creating a playbook run which allows an authenticated team member to create runs in teams where they lack permission via specifying a different team ID in the run creation API request. Mattermost Advisory ID: MMSA-2026-00629.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4055
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
