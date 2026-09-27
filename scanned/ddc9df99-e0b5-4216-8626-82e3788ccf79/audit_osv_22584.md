# [M] CVE-2022-32228

## Summary
Severity: Medium
Advisory: CVE-2022-32228
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-32228
Type: osv

## Details
An information disclosure vulnerability exists in Rocket.Chat <v5, <v4.8.2 and <v4.7.5 since the getReadReceipts Meteor server method does not properly filter user inputs that are passed to MongoDB queries, allowing $regex queries to enumerate arbitrary Message IDs.

## References
- https://hackerone.com/reports/1377105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32228.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32228
