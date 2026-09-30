# [M] Insecure Direct Object Reference in /plugins/focalboard/ api/v2/users of Mattermost Boards

## Summary
Severity: Medium
Advisory: CVE-2023-6202
Aliases: GHSA-85jj-c9jr-9jhx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-6202
Type: osv

## Details
Mattermost fails to perform proper authorization in the /plugins/focalboard/api/v2/users endpoint allowing an attacker who is a guest user and knows the ID of another user to get their information (e.g. name, surname, nickname) via Mattermost Boards.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6202.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6202
