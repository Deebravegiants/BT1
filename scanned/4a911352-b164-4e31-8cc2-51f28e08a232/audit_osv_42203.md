# [M] Unscoped updates to other playbooks' metric configuration

## Summary
Severity: Medium
Advisory: CVE-2026-6541
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-6541
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.1, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to restrict metric configuration changes to the playbook being saved, which allows an authenticated user with team access to alter another user’s playbook metric settings via a crafted import or update request with a foreign metric ID. Mattermost Advisory ID: MMSA-2026-00653

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6541.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-6541
