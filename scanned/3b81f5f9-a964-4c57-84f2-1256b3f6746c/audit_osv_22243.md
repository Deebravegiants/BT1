# [M] Guest accounts can list all public channels

## Summary
Severity: Medium
Advisory: CVE-2022-2408
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-07-14
Source: https://osv.dev/vulnerability/CVE-2022-2408
Type: osv

## Details
The Guest account feature in Mattermost version 6.7.0 and earlier fails to properly restrict the permissions, which allows a guest user to fetch a list of all public channels in the team, in spite of not being part of those channels.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2408.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2408
