# [M] IDOR: Accessing playbook runs via the Playbooks Runs API

## Summary
Severity: Medium
Advisory: CVE-2023-27263
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-02-27
Source: https://osv.dev/vulnerability/CVE-2023-27263
Type: osv

## Details
A missing permissions check in the /plugins/playbooks/api/v0/runs API in Mattermost allows an attacker to list and view playbooks belonging to a team they are not a member of.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27263.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27263
