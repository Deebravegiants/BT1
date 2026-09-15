# [H] IDOR: Updating a playbook via the Playbooks API

## Summary
Severity: High
Advisory: CVE-2023-27264
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2023-02-27
Source: https://osv.dev/vulnerability/CVE-2023-27264
Type: osv

## Details
A missing permissions check in Mattermost Playbooks in Mattermost allows an attacker to modify a playbook via the /plugins/playbooks/api/v0/playbooks/[playbookID] API.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27264.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27264
