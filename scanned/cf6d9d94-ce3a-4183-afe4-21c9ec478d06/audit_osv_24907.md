# [M] CVE-2023-28357

## Summary
Severity: Medium
Advisory: CVE-2023-28357
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-05-11
Source: https://osv.dev/vulnerability/CVE-2023-28357
Type: osv

## Details
A vulnerability has been identified in Rocket.Chat, where the ACL checks in the Slash Command /mute occur after checking whether a user is a member of a given channel, leaking private channel members to unauthorized users. This allows authenticated users to enumerate whether a username is a member of a channel that they do not have access to.

## References
- https://hackerone.com/reports/1445810
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28357.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28357
