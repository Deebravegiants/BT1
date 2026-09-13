# [M] Ephemeral messages return private channel contents in permalink previews

## Summary
Severity: Medium
Advisory: CVE-2023-2792
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2792
Type: osv

## Details
Mattermost fails to sanitize ephemeral error messages, allowing an attacker to obtain arbitrary message contents by a specially crafted /groupmsg command.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2792.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2792
