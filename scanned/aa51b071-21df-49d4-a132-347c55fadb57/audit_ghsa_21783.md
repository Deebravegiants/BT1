# [H] Infinite Loop in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-m7jv-hq7h-mq7c
CVE: CVE-2020-13935
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-08
Source: https://github.com/advisories/GHSA-m7jv-hq7h-mq7c
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0-M1 <10.0.0-M7
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.37
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.57
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.27 <7.0.105
- Maven: `org.apache.tomcat.embed:tomcat-embed-websocket` — affected >=7.0.27 <7.0.105
- Maven: `org.apache.tomcat.embed:tomcat-embed-websocket` — affected >=8.5.0 <8.5.57
- Maven: `org.apache.tomcat.embed:tomcat-embed-websocket` — affected >=9.0.0.M1 <9.0.37
- Maven: `org.apache.tomcat.embed:tomcat-embed-websocket` — affected >=10.0.0-M1 <10.0.0-M7
- Maven: `org.apache.tomcat:tomcat-websocket` — affected >=10.0.0-M1 <10.0.0-M7
- Maven: `org.apache.tomcat:tomcat-websocket` — affected >=9.0.0.M1 <9.0.37
- Maven: `org.apache.tomcat:tomcat-websocket` — affected >=8.5.0 <8.5.57
- Maven: `org.apache.tomcat:tomcat-websocket` — affected >=7.0.27 <7.0.105

## Details
The payload length in a WebSocket frame was not correctly validated in Apache Tomcat 10.0.0-M1 to 10.0.0-M6, 9.0.0.M1 to 9.0.36, 8.5.0 to 8.5.56 and 7.0.27 to 7.0.104. Invalid payload lengths could trigger an infinite loop. Multiple requests with invalid payload lengths could lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13935
- https://github.com/apache/tomcat/commit/12d715676038efbf9c728af10163f8277fc019d5
- https://github.com/apache/tomcat/commit/1c1c77b0efb667cea80b532440b44cea1dc427c3
- https://github.com/apache/tomcat/commit/40fa74c74822711ab878079d0a69f7357926723d
- https://github.com/apache/tomcat/commit/4c04982870d6e730c38e21e58fb653b7cf723784
- https://github.com/apache/tomcat/commit/f9f75c14678b68633f79030ddf4ff827f014cc84
- https://tomcat.apache.org/security-9.html
- https://usn.ubuntu.com/4448-1
- https://usn.ubuntu.com/4596-1
- https://www.debian.org/security/2020/dsa-4727
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-7.html
- https://tomcat.apache.org/security-10.html
