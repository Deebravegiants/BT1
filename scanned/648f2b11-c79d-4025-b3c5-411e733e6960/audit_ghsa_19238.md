# [M] Apache ActiveMQ: Unchecked buffer length can cause excessive memory allocation

## Summary
Severity: Medium
Advisory: GHSA-whxr-3p84-rf3c
CVE: CVE-2025-27533
CWE: CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-07
Source: https://github.com/advisories/GHSA-whxr-3p84-rf3c
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=0 <5.16.8
- Maven: `org.apache.activemq:activemq-client` — affected >=0 <5.16.8
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.17.0 <5.17.7
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=5.18.0 <5.18.7
- Maven: `org.apache.activemq:activemq-openwire-legacy` — affected >=6.0.0 <6.1.6
- Maven: `org.apache.activemq:activemq-client` — affected >=5.17.0 <5.17.7
- Maven: `org.apache.activemq:activemq-client` — affected >=5.18.0 <5.18.7
- Maven: `org.apache.activemq:activemq-client` — affected >=6.0.0 <6.1.6

## Details
Memory Allocation with Excessive Size Value vulnerability in Apache ActiveMQ.

During unmarshalling of OpenWire commands the size value of buffers was not properly validated which could lead to excessive memory allocation and be exploited to cause a denial of service (DoS) by depleting process memory, thereby affecting applications and services that rely on the availability of the ActiveMQ broker when not using mutual TLS connections.
This issue affects Apache ActiveMQ: from 6.0.0 before 6.1.6, from 5.18.0 before 5.18.7, from 5.17.0 before 5.17.7, before 5.16.8. ActiveMQ 5.19.0 is not affected.

Users are recommended to upgrade to version 6.1.6+, 5.19.0+,  5.18.7+, 5.17.7, or 5.16.8 or which fixes the issue.

Existing users may implement mutual TLS to mitigate the risk on affected brokers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27533
- https://github.com/apache/activemq/commit/fc4372b9f0f72b8b5eed917f0019c5cea45c5d06
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-6596
- https://lists.apache.org/thread/8hcm25vf7mchg4zbbhnlx2lc5bs705hg
- https://lists.debian.org/debian-lts-announce/2025/06/msg00020.html
- http://www.openwall.com/lists/oss-security/2025/05/06/1
