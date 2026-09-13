# [C] Apache HugeGraph-Server: Command execution in gremlin

## Summary
Severity: Critical
Advisory: GHSA-29rc-vq7f-x335
CVE: CVE-2024-27348
CWE: CWE-284, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-29rc-vq7f-x335
Type: github-advisory

## Affected
- Maven: `org.apache.hugegraph:hugegraph-api` — affected >=1.0.0 <1.3.0
- Maven: `org.apache.hugegraph:hugegraph-core` — affected >=1.0.0 <1.3.0

## Details
RCE-Remote Command Execution vulnerability in Apache HugeGraph-Server.This issue affects Apache HugeGraph-Server: from 1.0.0 before 1.3.0 in Java8 & Java11

Users are recommended to upgrade to version 1.3.0 with Java11 & enable the Auth system, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27348
- https://github.com/apache/incubator-hugegraph/commit/713d88d1fd9953c3c3e3f130389501910ba40e1d
- https://github.com/apache/incubator-hugegraph
- https://hugegraph.apache.org/docs/config/config-authentication/#configure-user-authentication
- https://lists.apache.org/thread/nx6g6htyhpgtzsocybm242781o8w5kq9
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2024-27348
- https://www.vicarius.io/vsociety/posts/remote-code-execution-vulnerability-in-apache-hugegraph-server-cve-2024-27348
- http://www.openwall.com/lists/oss-security/2024/04/22/3
