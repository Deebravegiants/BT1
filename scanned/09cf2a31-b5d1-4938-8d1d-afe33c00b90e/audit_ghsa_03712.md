# [M] Apache Thrift Node.js static web server sandbox escape

## Summary
Severity: Medium
Advisory: GHSA-vx85-mj8c-4qm6
CVE: CVE-2018-11798
CWE: CWE-538
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-01-17
Source: https://github.com/advisories/GHSA-vx85-mj8c-4qm6
Type: github-advisory

## Affected
- Maven: `org.apache.thrift:libthrift` — affected >=0.9.2 <0.12.0

## Details
The Apache Thrift Node.js static web server in versions 0.9.2 through 0.11.0 have been determined to contain a security vulnerability in which a remote user has the ability to access files outside the set webservers docroot path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11798
- https://github.com/apache/thrift/pull/1606
- https://github.com/apache/thrift/commit/2a2b72f6c8aef200ecee4984f011e06052288ff2
- https://access.redhat.com/errata/RHSA-2019:1545
- https://access.redhat.com/errata/RHSA-2019:3140
- https://github.com/advisories/GHSA-vx85-mj8c-4qm6
- https://issues.apache.org/jira/browse/THRIFT-4647
- https://lists.apache.org/thread.html/6e9edd282684896cedf615fb67a02bebfe6007f2d5baf03ba52e34fd@%3Cuser.thrift.apache.org%3E
- https://web.archive.org/web/20200227094236/http://www.securityfocus.com/bid/106501
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
