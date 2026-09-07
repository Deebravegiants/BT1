# [M] Apache Zeppelin: Cron arbitrary user impersonation with improper privileges

## Summary
Severity: Medium
Advisory: GHSA-g44m-x5h7-fr5q
CVE: CVE-2024-31865
CWE: CWE-20, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-g44m-x5h7-fr5q
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.8.2 <0.11.1

## Details
Improper Input Validation vulnerability in Apache Zeppelin.

The attackers can call updating cron API with invalid or improper privileges so that the notebook can run with the privileges.

This issue affects Apache Zeppelin: from 0.8.2 before 0.11.1.

Users are recommended to upgrade to version 0.11.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31865
- https://github.com/apache/zeppelin/pull/4631
- https://github.com/apache/zeppelin/commit/49e2740a1d83d58d2401ccf175fc91ffebfb0892
- https://github.com/apache/zeppelin
- https://lists.apache.org/thread/slm1sf0slwc11f4m4r0nd6ot2rf7w81l
- http://www.openwall.com/lists/oss-security/2024/04/09/9
