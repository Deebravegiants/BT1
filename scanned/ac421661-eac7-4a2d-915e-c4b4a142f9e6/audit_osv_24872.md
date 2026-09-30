# [M] Channel commands execution doesn't properly verify permissions

## Summary
Severity: Medium
Advisory: CVE-2023-2786
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2786
Type: osv

## Details
Mattermost fails to properly check the permissions when executing commands allowing a member with no permissions to post a message in a channel to actually post it by executing channel commands.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2786.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2786
