# [C] Spring Framework has Improperly Implemented Security Check for Standard

## Summary
Severity: Critical
Advisory: GHSA-3rmv-2pg5-xvqj
CVE: CVE-2018-1275
CWE: CWE-358, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-3rmv-2pg5-xvqj
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-messaging` — affected >=0 <4.3.16.RELEASE
- Maven: `org.springframework:spring-messaging` — affected >=5.0.0.RELEASE <5.0.5.RELEASE

## Details
Spring Framework, versions 5.0 prior to 5.0.5 and versions 4.3 prior to 4.3.16 and older unsupported versions, allow applications to expose STOMP over WebSocket endpoints with a simple, in-memory STOMP broker through the spring-messaging module. A malicious user (or attacker) can craft a message to the broker that can lead to a remote code execution attack. This CVE addresses the partial fix for CVE-2018-1270 in the 4.3.x branch of the Spring Framework.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1275
- https://github.com/spring-projects/spring-framework/commit/0009806debb578e884f6dc98bd1f2dc668020021
- https://github.com/spring-projects/spring-framework/commit/e0de9126ed8cf25cf141d3e66420da94e350708a
- https://access.redhat.com/errata/RHSA-2018:1320
- https://access.redhat.com/errata/RHSA-2018:2939
- https://github.com/spring-projects/spring-framework
- https://lists.apache.org/thread.html/4ed49b103f64a0cecb38064f26cbf1389afc12124653da2d35166dbe@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/ab825fcade0b49becfa30235b3d54f4a51bb74ea96b6c9adb5d1378c@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/dcf8599b80e43a6b60482607adb76c64672772dc2d9209ae2170f369@%3Cissues.activemq.apache.org%3E
- https://pivotal.io/security/cve-2018-1275
- https://web.archive.org/web/20190901081835/http://www.securitytracker.com/id/1041301
- https://web.archive.org/web/20200227033125/http://www.securityfocus.com/bid/103771
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
