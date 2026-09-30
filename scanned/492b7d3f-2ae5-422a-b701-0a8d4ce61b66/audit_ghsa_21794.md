# [H] Exposure of Sensitive Information to an Unauthorized Actor in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-vvw4-rfwf-p6hx
CVE: CVE-2020-17527
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-vvw4-rfwf-p6hx
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.0.0-M1 <10.0.0-M10
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0-M1 <9.0.40
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=8.5.0 <8.5.60

## Details
While investigating bug 64830 it was discovered that Apache Tomcat 10.0.0-M1 to 10.0.0-M9, 9.0.0-M1 to 9.0.39 and 8.5.0 to 8.5.59 could re-use an HTTP request header value from the previous stream received on an HTTP/2 connection for the request associated with the subsequent stream. While this would most likely lead to an error and the closure of the HTTP/2 connection, it is possible that information could leak between requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17527
- https://github.com/apache/tomcat/commit/21e3408671aac7e0d7e264e720cac8b1b189eb29
- https://github.com/apache/tomcat/commit/8d2fe6894d6e258a6d615d7f786acca80e6020cb
- https://github.com/apache/tomcat/commit/d56293f816d6dc9e2b47107f208fa9e95db58c65
- https://lists.apache.org/thread.html/rce5ac9a40173651d540babce59f6f3825f12c6d4e886ba00823b11e5@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rce5ac9a40173651d540babce59f6f3825f12c6d4e886ba00823b11e5@%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rd5babd13d7a350b369b2f647b4dd32ce678af42f9aba5389df1ae6ca@%3Cusers.tomcat.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/12/msg00022.html
- https://security.gentoo.org/glsa/202012-23
- https://security.netapp.com/advisory/ntap-20201210-0003
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
- https://www.debian.org/security/2021/dsa-4835
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://lists.apache.org/thread.html/rce5ac9a40173651d540babce59f6f3825f12c6d4e886ba00823b11e5%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rca833c6d42b7b9ce1563488c0929f29fcc95947d86e5e740258c8937@%3Cdev.tomcat.apache.org%3E
