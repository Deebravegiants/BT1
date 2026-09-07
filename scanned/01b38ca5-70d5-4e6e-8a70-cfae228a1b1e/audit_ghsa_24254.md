# [H] Apache Thrift Go Library Command Injection

## Summary
Severity: High
Advisory: GHSA-r4m4-pmvw-m6j5
CVE: CVE-2016-5397
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r4m4-pmvw-m6j5
Type: github-advisory

## Affected
- Go: `github.com/apache/thrift` — affected >=0 <0.10.0

## Details
The Apache Thrift Go client library exposed the potential during code generation for command injection due to using an external formatting tool. Affected Apache Thrift 0.9.3 and older, Fixed in Apache Thrift 0.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5397
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2019:3140
- https://issues.apache.org/jira/browse/THRIFT-3893
- https://lists.apache.org/thread.html/r4d3f1d3e333d9c2b2f6e6ae8ed8750d4de03410ac294bcd12c7eefa3@%3Ccommits.cassandra.apache.org%3E
- https://web.archive.org/web/20210124141102/http://www.securityfocus.com/bid/103025
- http://mail-archives.apache.org/mod_mbox/thrift-user/201701.mbox/raw/%3CCANyrgvc3W%3DMJ9S-hMZecPNzxkyfgNmuSgVfW2hdDSz5ke%2BOPhQ%40mail.gmail.com%3E
