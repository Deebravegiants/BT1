# [M] CVE-2022-35247

## Summary
Severity: Medium
Advisory: CVE-2022-35247
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-35247
Type: osv

## Details
A information disclosure vulnerability exists in Rocket.chat <v5, <v4.8.2 and <v4.7.5 where the lack of ACL checks in the getRoomRoles Meteor method leak channel members with special roles to unauthorized clients.

## References
- https://hackerone.com/reports/1447440
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35247.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-35247
