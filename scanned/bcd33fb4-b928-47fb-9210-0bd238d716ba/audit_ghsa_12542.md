# [H] Apache NiFi vulnerable to Code Injection

## Summary
Severity: High
Advisory: GHSA-xm2m-2q6h-22jw
CVE: CVE-2023-34468
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-xm2m-2q6h-22jw
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-dbcp-base` — affected >=0.0.2 <1.22.0
- Maven: `org.apache.nifi:nifi-hikari-dbcp-service` — affected >=0.0.2 <1.22.0
- Maven: `org.apache.nifi:nifi-dbcp-service-nar` — affected >=0.0.2 <1.22.0

## Details
The DBCPConnectionPool and HikariCPConnectionPool Controller Services in Apache NiFi 0.0.2 through 1.21.0 allow an authenticated and authorized user to configure a Database URL with the H2 driver that enables custom code execution.

The resolution validates the Database URL and rejects H2 JDBC locations.

You are recommended to upgrade to version 1.22.0 or later which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34468
- https://github.com/apache/nifi/pull/7349
- https://github.com/apache/nifi/commit/4faf3ea59895e7e153db3f8f61147ff70a254361
- https://exceptionfactory.com/posts/2023/10/07/firsthand-analysis-of-apache-nifi-vulnerability-cve-2023-34468
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-11653
- https://lists.apache.org/thread/7b82l4f5blmpkfcynf3y6z4x1vqo59h8
- https://nifi.apache.org/security.html#CVE-2023-34468
- https://www.cyfirma.com/outofband/apache-nifi-cve-2023-34468-rce-vulnerability-analysis-and-exploitation
- http://packetstormsecurity.com/files/174398/Apache-NiFi-H2-Connection-String-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2023/06/12/3
