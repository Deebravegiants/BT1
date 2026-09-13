# [H] Apache Zeppelin exposes server resources to unauthenticated attackers

## Summary
Severity: High
Advisory: GHSA-7pgf-ppxw-8624
CVE: CVE-2024-41169
CWE: CWE-664
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-07-12
Source: https://github.com/advisories/GHSA-7pgf-ppxw-8624
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin-interpreter` — affected >=0.10.1 <0.12.0
- Maven: `org.apache.zeppelin:zeppelin-server` — affected >=0.10.1 <0.12.0

## Details
The attacker can use the raft server protocol in an unauthenticated way. The attacker can see the server's resources, including directories and files.

This issue affects Apache Zeppelin: from 0.10.1 up to 0.12.0.

Users are recommended to upgrade to version 0.12.0, which fixes the issue by removing the Cluster Interpreter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41169
- https://github.com/apache/zeppelin/pull/4841
- https://github.com/apache/zeppelin
- https://issues.apache.org/jira/browse/ZEPPELIN-6101
- https://lists.apache.org/thread/moyym04993c8owh4h0qj98r43tbo8qdd
- http://www.openwall.com/lists/oss-security/2025/07/13/1
