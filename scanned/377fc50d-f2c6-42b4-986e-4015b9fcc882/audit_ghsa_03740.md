# [M] Improper Input Validation and Missing Authentication for Critical Function in Apache ActiveMQ

## Summary
Severity: Medium
Advisory: GHSA-jvpp-hxjj-5ccc
CVE: CVE-2015-7559
CWE: CWE-20, CWE-306
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-08-01
Source: https://github.com/advisories/GHSA-jvpp-hxjj-5ccc
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-client` — affected >=0 <5.14.5

## Details
It was found that the Apache ActiveMQ client before 5.14.5 exposed a remote shutdown command in the ActiveMQConnection class. An attacker logged into a compromised broker could use this flaw to achieve denial of service on a connected client.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7559
- https://github.com/apache/activemq/commit/b8fc78ec6c367cbe2a40a674eaec64ac3d7d1ec
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2015-7559
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-6470
