# [M] Playbooks lets you edit arbitrary posts

## Summary
Severity: Medium
Advisory: CVE-2023-2791
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2791
Type: osv

## Details
When creating a playbook run via the /dialog API, Mattermost fails to validate all parameters, allowing an authenticated attacker to edit an arbitrary channel post.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2791.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2791
