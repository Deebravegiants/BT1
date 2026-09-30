# [M] Apache HBase: Missing scanner instance owner check in thrift delegation service

## Summary
Severity: Medium
Advisory: CVE-2026-49326
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-49326
Type: osv

## Details
Missing Authorization vulnerability in Apache HBase thrift and rest delegation service.

A scan operation in thrift/rest service has 3 steps, open, fetch(possible multiple times), close.
The open step will return an id which will be passed back to server for identifying the scanner instances stored at server side.
We missed the owner check in fetch and close steps which means a user can fetch rows from the scanner which is opened by other users, and close scanners which belongs to other users.

This issue affects Apache HBase:from 3.0.0-alpha-1 through 3.0.0-beta-1, from 2.6.0 through 2.6.5, from 2.5.0 through 2.5.14, through 2.4.*.

Users are recommended to upgrade to version 3.0.0-beta-2, 2.6.6 and 2.5.15, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/23
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49326.json
- https://lists.apache.org/thread/f4l4sjgwb9tb04cqnkpgl6gy3slgvcsj
- https://nvd.nist.gov/vuln/detail/CVE-2026-49326
