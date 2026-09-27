# [M] Post actions can run playbook checklist task commands

## Summary
Severity: Medium
Advisory: CVE-2024-36255
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-36255
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.6.x <= 9.6.1 and 8.1.x <= 8.1.12 fail to perform proper input validation on post actions which allows an attacker to run a playbook checklist task command as another user via creating and sharing a deceptive post action that unexpectedly runs a slash command in some arbitrary channel.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36255.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36255
