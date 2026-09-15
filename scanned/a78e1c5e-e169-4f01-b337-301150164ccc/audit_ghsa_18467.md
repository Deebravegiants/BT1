# [H] Apache Tomcat Coyote vulnerable to Denial of Service via excessive HTTP/2 streams

## Summary
Severity: High
Advisory: GHSA-25xr-qj8w-c4vf
CVE: CVE-2025-53506
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-25xr-qj8w-c4vf
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.0-M1 <11.0.9
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.0-M1 <10.1.43
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.107
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.43
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.9

## Details
Uncontrolled Resource Consumption vulnerability in Apache Tomcat if an HTTP/2 client did not acknowledge the initial settings frame that reduces the maximum permitted concurrent streams.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.8, from 10.1.0-M1 through 10.1.42, from 9.0.0.M1 through 9.0.106. The following versions were EOL at the time the CVE was created but are known to be affected: 8.5.0 through 8.5.100.

Users are recommended to upgrade to version 11.0.9, 10.1.43 or 9.0.107, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53506
- https://github.com/apache/tomcat/commit/2aa6261276ebe50b99276953591e3a2be7898bdb
- https://github.com/apache/tomcat/commit/434772930f362145516dd60681134e7f0cf8115b
- https://github.com/apache/tomcat/commit/be8f330f83ceddaf3baeed57522e571572b6b99b
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/p09775q0rd185m6zz98krg0fp45j8kr0
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- http://www.openwall.com/lists/oss-security/2025/07/10/13
