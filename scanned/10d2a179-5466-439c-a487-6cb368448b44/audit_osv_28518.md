# [M] AD/LDAP Group Members Leak

## Summary
Severity: Medium
Advisory: CVE-2024-34029
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-34029
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.7.x <= 9.7.1 and 8.1.x <= 8.1.12 fail to perform a proper authorization check in the /api/v4/groups/<group-id>/channels/<channel-id>/link endpoint which allows a user to learn the members of an AD/LDAP group that is linked to a team by adding the group to a channel, even if the user has no access to the team.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34029.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34029
