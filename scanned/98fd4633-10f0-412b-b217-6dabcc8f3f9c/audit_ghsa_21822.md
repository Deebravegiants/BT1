# [H] Uncontrolled Resource Consumption in Apache Tomcat

## Summary
Severity: High
Advisory: GHSA-53hp-jpwq-2jgq
CVE: CVE-2020-11996
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-53hp-jpwq-2jgq
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=10.0.0-M1 <10.0.0-M5
- Maven: `org.apache.tomcat:tomcat` — affected >=9.0.0.M1 <9.0.35
- Maven: `org.apache.tomcat:tomcat` — affected >=8.5.0 <8.5.55
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.0.0-M1 <10.0.0-M5
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.35
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=8.5.0 <8.5.55

## Details
A specially crafted sequence of HTTP/2 requests sent to Apache Tomcat 10.0.0-M1 to 10.0.0-M5, 9.0.0.M1 to 9.0.35 and 8.5.0 to 8.5.55 could trigger high CPU usage for several seconds. If a sufficient number of such requests were made on concurrent HTTP/2 connections, the server could become unresponsive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11996
- https://github.com/apache/tomcat/commit/9434a44d3449d620b1be70206819f8275b4a7509
- https://github.com/apache/tomcat/commit/9a0231683a77e2957cea0fdee88b193b30b0c976
- https://github.com/apache/tomcat/commit/c8acd2ab7371e39aeca7c306f3b5380f00afe552
- https://lists.apache.org/thread.html/rb820f1a2a02bf07414be12c653c2ab5321fd87b9bf6c5e635c53ff4b@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rc80b96b4b96618b2b7461cb90664a428cfd6605eea9f74e51b792542@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/rea65d6ef2e45dd1c45faae83922042732866c7b88fa109b76c83db52@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/ref0339792ac6dac1dba83c071a727ad72380899bde60f6aaad4031b9@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/07/msg00010.html
- https://security.netapp.com/advisory/ntap-20200709-0002
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-8.html
- https://tomcat.apache.org/security-9.html
- https://usn.ubuntu.com/4596-1
- https://www.debian.org/security/2020/dsa-4727
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://lists.apache.org/thread.html/rb4ee49ecc4c59620ffd5e66e84a17e526c2c3cfa95d0cd682d90d338@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/ra7092f7492569b39b04ec0decf52628ba86c51f15efb38f5853e2760@%3Cnotifications.ofbiz.apache.org%3E
- https://lists.apache.org/thread.html/r9ad911fe49450ed9405827af0e7a74104041081ff91864b1f2546bbd@%3Cnotifications.ofbiz.apache.org%3E
