# [H] Missing Release of Resource after Effective Lifetime in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-wph7-x527-w3h5
CVE: CVE-2021-42340
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-15
Source: https://github.com/advisories/GHSA-wph7-x527-w3h5
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.1.0-M1 <10.1.0-M6
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0-M1 <10.0.12
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.40 <9.0.54
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.60 <8.5.72

## Details
The fix for bug 63362 present in Apache Tomcat 10.1.0-M1 to 10.1.0-M5, 10.0.0-M1 to 10.0.11, 9.0.40 to 9.0.53 and 8.5.60 to 8.5.71 introduced a memory leak. The object introduced to collect metrics for HTTP upgrade connections was not released for WebSocket connections once the connection was closed. This created a memory leak that, over time, could lead to a denial of service via an OutOfMemoryError.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-42340
- https://github.com/apache/tomcat/commit/31d62426645824bdfe076a0c0eafa904d90b4fb9
- https://github.com/apache/tomcat/commit/80f1438ec45e77a07b96419808971838d259eb47
- https://github.com/apache/tomcat/commit/d27535bdee95d252418201eb21e9d29476aa6b6a
- https://github.com/apache/tomcat/commit/d5a6660cba7f51589468937bf3bbad4db7810371
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.debian.org/security/2021/dsa-5009
- https://tomcat.apache.org/security-9.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-10.html
- https://security.netapp.com/advisory/ntap-20211104-0001
- https://security.gentoo.org/glsa/202208-34
- https://lists.apache.org/thread.html/r83a35be60f06aca2065f188ee542b9099695d57ced2e70e0885f905c%40%3Cannounce.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r8097a2d1550aa78e585fc77e602b9046e6d4099d8d132497c5387784@%3Ccommits.myfaces.apache.org%3E
- https://kc.mcafee.com/corporate/index?page=content&id=SB10379
- https://github.com/apache/tomcat
