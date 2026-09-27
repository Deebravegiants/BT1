# [M] Apache Tomcat Request and/or response mix-up

## Summary
Severity: Medium
Advisory: GHSA-qvf5-hvjx-wm27
CVE: CVE-2024-52317
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-qvf5-hvjx-wm27
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.92 <9.0.96
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.92 <9.0.96
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.27 <10.1.31
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M23 <11.0.0
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.27 <10.1.31
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.0-M23 <11.0.0

## Details
Incorrect object re-cycling and re-use vulnerability in Apache Tomcat. Incorrect recycling of the request and response used by HTTP/2 requests could lead to request and/or response mix-up between users.

This issue affects Apache Tomcat: from 11.0.0-M23 through 11.0.0-M26, from 10.1.27 through 10.1.30, from 9.0.92 through 9.0.95.

Users are recommended to upgrade to version 11.0.0, 10.1.31 or 9.0.96, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52317
- https://github.com/apache/tomcat/commit/146f94f87ea398fb592c7a20a5ccbef95e9dd72b
- https://github.com/apache/tomcat/commit/47307ee27abcdea2ee40e33897aca760083de46a
- https://github.com/apache/tomcat/commit/9e840ccacb40881c03a03b1e0746bfba7369b3bd
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/ty376mrxy1mmxtw3ogo53nc9l3co3dfs
- https://security.netapp.com/advisory/ntap-20250124-0004
- http://www.openwall.com/lists/oss-security/2024/11/18/3
