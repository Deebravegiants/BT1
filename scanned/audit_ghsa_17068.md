# [M] Apache Pulsar: Improper Authorization For Topic-Level Policy Management

## Summary
Severity: Medium
Advisory: GHSA-g627-r579-rw35
CVE: CVE-2024-28098
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-12
Source: https://github.com/advisories/GHSA-g627-r579-rw35
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.2.0 <3.2.1
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.1.0 <3.1.3
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=3.0.0 <3.0.3
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.11.0 <2.11.4
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.7.1 <2.10.6

## Details
The vulnerability allows authenticated users with only produce or consume permissions to modify topic-level policies, such as retention, TTL, and offloading settings. These management operations should be restricted to users with the tenant admin role or super user role.

This issue affects Apache Pulsar versions from 2.7.1 to 2.10.5, from 2.11.0 to 2.11.3, from 3.0.0 to 3.0.2, from 3.1.0 to 3.1.2, and 3.2.0. 

2.10 Apache Pulsar users should upgrade to at least 2.10.6.
2.11 Apache Pulsar users should upgrade to at least 2.11.4.
3.0 Apache Pulsar users should upgrade to at least 3.0.3.
3.1 Apache Pulsar users should upgrade to at least 3.1.3.
3.2 Apache Pulsar users should upgrade to at least 3.2.1.

Users operating versions prior to those listed above should upgrade to the aforementioned patched versions or newer versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28098
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/3m6923y3wxpdcs9346sjvt8ql9swqc2z
- https://pulsar.apache.org/security/CVE-2024-28098
- http://www.openwall.com/lists/oss-security/2024/03/12/12
