# [M] Apache NiFi Insufficient Property Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-23qf-3jf9-h3q9
CVE: CVE-2023-40037
CWE: CWE-184, CWE-697
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-19
Source: https://github.com/advisories/GHSA-23qf-3jf9-h3q9
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi-dbcp-base` — affected >=1.21.0 <1.23.1
- Maven: `org.apache.nifi:nifi-jms-processors` — affected >=1.21.0 <1.23.1
- Maven: `org.apache.nifi:nifi-dbcp-service-api` — affected >=1.21.0 <1.23.1
- Maven: `org.apache.nifi:nifi-dbcp-service-bundle` — affected >=1.21.0 <1.23.1

## Details
Apache NiFi 1.21.0 through 1.23.0 support JDBC and JNDI JMS access in several Processors and Controller Services with connection URL validation that does not provide sufficient protection against crafted inputs. An authenticated and authorized user can bypass connection URL validation using custom input formatting. The resolution enhances connection URL validation and introduces validation for additional related properties. Upgrading to Apache NiFi 1.23.1 is the recommended mitigation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40037
- https://github.com/apache/nifi/pull/7586
- https://github.com/apache/nifi/commit/064550aacc189f39d7ddd2c0446068adf250f1bf
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-11920
- https://lists.apache.org/thread/bqbjlrs2p5ghh8sbk5nsxb8xpf9l687q
- https://nifi.apache.org/security.html#CVE-2023-40037
- http://www.openwall.com/lists/oss-security/2023/08/18/2
