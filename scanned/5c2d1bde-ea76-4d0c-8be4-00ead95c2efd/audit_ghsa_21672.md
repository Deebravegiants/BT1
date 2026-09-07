# [M] Cross-site Scripting (XSS) in Apache ActiveMQ Artemis

## Summary
Severity: Medium
Advisory: GHSA-3h2h-xqr2-2jp7
CVE: CVE-2020-13932
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-3h2h-xqr2-2jp7
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-artemis` — affected >=2.5.0 <2.14.0

## Details
In Apache ActiveMQ Artemis 2.5.0 to 2.13.0, a specially crafted MQTT packet which has an XSS payload as client-id or topic name can exploit this vulnerability. The XSS payload is being injected into the admin console's browser. The XSS payload is triggered in the diagram plugin; queue node and the info section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13932
- https://activemq.apache.org/security-advisories.data/CVE-2020-13932-announcement.txt
- https://lists.apache.org/thread.html/r7fcedcc89e5f296b174d6b8c1438c607c30d809c04292e5732d6e4eb%40%3Cusers.activemq.apache.org%3E
- https://lists.apache.org/thread.html/r7fcedcc89e5f296b174d6b8c1438c607c30d809c04292e5732d6e4eb@%3Cusers.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088@%3Ccommits.activemq.apache.org%3E
