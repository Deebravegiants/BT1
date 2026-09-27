# [H] Uncontrolled Resource Consumption in org.eclipse.jetty:jetty-server

## Summary
Severity: High
Advisory: GHSA-h2f4-v4c4-6wx4
CVE: CVE-2018-12545
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-03-28
Source: https://github.com/advisories/GHSA-h2f4-v4c4-6wx4
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.12.v20180830
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.25.v20180904

## Details
In Eclipse Jetty version 9.3.x and 9.4.x, the server is vulnerable to Denial of Service conditions if a remote client sends either large SETTINGs frames container containing many settings, or many small SETTINGs frames. The vulnerability is due to the additional CPU and memory allocations required to handle changed settings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12545
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=538096
- https://github.com/advisories/GHSA-h2f4-v4c4-6wx4
- https://lists.apache.org/thread.html/13f5241048ec0bf966a6ddd306feaf40de5b20e1f09096b9cddeddf2@%3Ccommits.accumulo.apache.org%3E
- https://lists.apache.org/thread.html/70744fe4faba8e2fa7e50a7fc794dd03cb28dad8b21e08ee59bb1606@%3Cdevnull.infra.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/febc94ffec9275dcda64633e0276a1400cd318e571009e4cda9b7a79@%3Cnotifications.accumulo.apache.org%3E
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CIS4LALKZNLF5X5IGNGRSKERG7FY4QG6
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
