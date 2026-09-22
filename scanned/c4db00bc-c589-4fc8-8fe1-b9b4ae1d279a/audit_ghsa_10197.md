# [M] Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ MQTT vulnerable to Integer Overflow or Wraparound

## Summary
Severity: Medium
Advisory: GHSA-xvqc-pp94-fmpx
CVE: CVE-2026-40046
CWE: CWE-190
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-xvqc-pp94-fmpx
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.4
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.4
- Maven: `org.apache.activemq:activemq-mqtt` — affected >=6.0.0 <6.2.4

## Details
Integer Overflow or Wraparound vulnerability in Apache ActiveMQ, Apache ActiveMQ All, Apache ActiveMQ MQTT.

The fix for "CVE-2025-66168: MQTT control packet remaining length field is not properly validated" was only applied to 5.19.2 (and future 5.19.x) releases but was missed for all 6.0.0+ versions. This issue affects Apache ActiveMQ: from 6.0.0 before 6.2.4; Apache ActiveMQ All: from 6.0.0 before 6.2.4; Apache ActiveMQ MQTT: from 6.0.0 before 6.2.4.

Users are recommended to upgrade to version 6.2.4 or a 5.19.x version starting with 5.19.2 or later (currently latest is 5.19.5), which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40046
- https://activemq.apache.org/security-advisories.data/CVE-2026-40046-announcement.txt
- https://lists.apache.org/thread/zdntj5rcgjjzrpow84o339lzldy68zrg
- https://www.cve.org/CVERecord?id=CVE-2025-66168
