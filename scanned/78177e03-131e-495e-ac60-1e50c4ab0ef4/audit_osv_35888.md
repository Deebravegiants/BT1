# [M] Missing run-state validation on finished playbook runs

## Summary
Severity: Medium
Advisory: CVE-2026-16046
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-16046
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21 fail to enforce run-state validation on write operations for finished playbook runs which allows a run participant to modify status, checklists, retrospective content, ownership, and participants on completed runs via REST and GraphQL API requests. Mattermost Advisory ID: MMSA-2026-00675

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16046.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-16046
