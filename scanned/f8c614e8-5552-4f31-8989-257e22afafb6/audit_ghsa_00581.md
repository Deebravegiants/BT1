# [C] SQL Injection in hive-jdbc

## Summary
Severity: Critical
Advisory: GHSA-jf2m-435m-mxw8
CVE: CVE-2018-1282
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-jf2m-435m-mxw8
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-jdbc` — affected >=0.7.1 <2.3.3

## Details
This vulnerability in Apache Hive JDBC driver 0.7.1 to 2.3.2 allows carefully crafted arguments to be used to bypass the argument escaping/cleanup that JDBC driver does in PreparedStatement implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1282
- https://github.com/advisories/GHSA-jf2m-435m-mxw8
- https://github.com/apache/hive
- https://lists.apache.org/thread.html/74bd2bff1827febb348dfb323986fa340d3bb97a315ab93c3ccc8299@%3Cdev.hive.apache.org%3E
- https://web.archive.org/web/20200227125536/http://www.securityfocus.com/bid/103751
