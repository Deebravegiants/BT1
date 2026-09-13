# [M] CVE-2022-32220

## Summary
Severity: Medium
Advisory: CVE-2022-32220
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32220
Type: osv

## Details
An information disclosure vulnerability exists in Rocket.Chat <v5 due to the getUserMentionsByChannel meteor server method discloses messages from private channels and direct messages regardless of the users access permission to the room.

## References
- https://hackerone.com/reports/1410246
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32220.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32220
