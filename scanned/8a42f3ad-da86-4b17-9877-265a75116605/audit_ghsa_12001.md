# [M] Mattermost fails to verify run_create permission for empty playbookId

## Summary
Severity: Medium
Advisory: GHSA-4pmx-622h-x359
CVE: CVE-2026-26304
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-4pmx-622h-x359
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-playbooks` — affected >=0 <1.41.1-0.20260316224925-705f54a81841

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2 fail to verify run_create permission for empty playbookId, which allows team members to create unauthorized runs via the playbook run API. Mattermost Advisory ID: MMSA-2025-00542

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26304
- https://github.com/mattermost/mattermost-plugin-playbooks/commit/705f54a818410f3612df3865bfde608ed471037e
- https://github.com/mattermost/mattermost-plugin-playbooks
- https://mattermost.com/security-updates
