# [M] CVE-2022-32226

## Summary
Severity: Medium
Advisory: CVE-2022-32226
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32226
Type: osv

## Details
An improper access control vulnerability exists in Rocket.Chat <v5, <v4.8.2 and <v4.7.5 due to input data in the getUsersOfRoom Meteor server method is not type validated, so that MongoDB query operator objects are accepted by the server, so that instead of a matching rid String a$regex query can be executed, bypassing the room access permission check for every but the first matching room.

## References
- https://hackerone.com/reports/1410357
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32226.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32226
