# [M] Apache Tomcat is vulnerable to resource exhaustion when using the APR/Native connector

## Summary
Severity: Medium
Advisory: GHSA-4j3c-42xv-3f84
CVE: CVE-2025-52434
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-4j3c-42xv-3f84
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0

## Details
Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition') vulnerability in Apache Tomcat when using the APR/Native connector. This was particularly noticeable with client initiated closes of HTTP/2 connections.

This issue affects Apache Tomcat: from 9.0.0.M1 through 9.0.106.  The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 through 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 9.0.107, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-52434
- https://github.com/apache/tomcat/commit/8a83c3c42d20762782678932c14005cd3397a018
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/gxgh65004f25y8519coth6w7vchww030
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- http://www.openwall.com/lists/oss-security/2025/07/10/11
