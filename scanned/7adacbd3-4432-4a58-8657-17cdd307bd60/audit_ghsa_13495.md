# [C] Apache ActiveMQ is vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-crg9-44h2-xw35
CVE: CVE-2023-46604
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H/E:H (CVSS_V3)
Published: 2023-10-27
Source: https://github.com/advisories/GHSA-crg9-44h2-xw35
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-client` — affected >=0 <5.15.16
- Maven: `org.apache.activemq:activemq-client` — affected >=5.16.0 <5.16.7
- Maven: `org.apache.activemq:activemq-client` — affected >=5.17.0 <5.17.6
- Maven: `org.apache.activemq:activemq-client` — affected >=5.18.0 <5.18.3
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.8.0 <5.15.16
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.16.0 <5.16.7
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.17.0 <5.17.6
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.18.0 <5.18.3

## Details
Apache ActiveMQ is vulnerable to Remote Code Execution.The vulnerability may allow a remote attacker with network access to a broker to run arbitrary shell commands by manipulating serialized class types in the OpenWire protocol to cause the broker to instantiate any class on the classpath. 

Users are recommended to upgrade to version 5.15.16, 5.16.7, 5.17.6, or 5.18.3, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46604
- https://github.com/apache/activemq/pull/1098
- https://github.com/apache/activemq/commit/22442b2385b1000312aec3d19e510131d595a5fc
- https://github.com/apache/activemq/commit/80089f9f476afab7d976f5fc37c5ab4aa0c2139d
- https://github.com/apache/activemq/commit/958330df26cf3d5cdb63905dc2c6882e98781d8f
- https://github.com/apache/activemq/commit/9905e2a5bf9862a049f94ce0a2465b0c7ad52436
- https://github.com/apache/activemq/commit/d0ccdd31544ada83185554c87c7aa141064020f0
- https://www.openwall.com/lists/oss-security/2023/10/27/5
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2023-46604
- https://security.netapp.com/advisory/ntap-20231110-0010
- https://packetstormsecurity.com/files/175676/Apache-ActiveMQ-Unauthenticated-Remote-Code-Execution.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00027.html
- https://lists.debian.org/debian-lts-announce/2023/11/msg00013.html
- https://issues.apache.org/jira/browse/AMQ-9370
- https://github.com/apache/activemq
- https://activemq.apache.org/security-advisories.data/CVE-2023-46604-announcement.txt
- https://activemq.apache.org/security-advisories.data/CVE-2023-46604
- http://packetstormsecurity.com/files/175676/Apache-ActiveMQ-Unauthenticated-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2024/Apr/18
- http://www.openwall.com/lists/oss-security/2023/10/27/5
