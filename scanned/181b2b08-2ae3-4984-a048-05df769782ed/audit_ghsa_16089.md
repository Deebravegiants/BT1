# [M] Apache Kafka Clients: Privilege escalation to filesystem read-access via automatic ConfigProvider

## Summary
Severity: Medium
Advisory: GHSA-2x2g-32r7-p4x8
CVE: CVE-2024-31141
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-19
Source: https://github.com/advisories/GHSA-2x2g-32r7-p4x8
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=2.3.0 <3.7.1

## Details
Files or Directories Accessible to External Parties, Improper Privilege Management vulnerability in Apache Kafka Clients.

Apache Kafka Clients accept configuration data for customizing behavior, and includes ConfigProvider plugins in order to manipulate these configurations. Apache Kafka also provides FileConfigProvider, DirectoryConfigProvider, and EnvVarConfigProvider implementations which include the ability to read from disk or environment variables.
In applications where Apache Kafka Clients configurations can be specified by an untrusted party, attackers may use these ConfigProviders to read arbitrary contents of the disk and environment variables.

In particular, this flaw may be used in Apache Kafka Connect to escalate from REST API access to filesystem/environment access, which may be undesirable in certain environments, including SaaS products.
This issue affects Apache Kafka Clients: from from 2.3.0 through 3.5.2, 3.6.0 through 3.6.2, and 3.7.0.


Users with affected applications are recommended to upgrade kafka-clients to version >=3.8.0, and set the JVM system property "org.apache.kafka.automatic.config.providers=none".
Users of Kafka Connect with one of the listed ConfigProvider implementations specified in their worker config are also recommended to add appropriate "allowlist.pattern" and "allowed.paths" to restrict their operation to appropriate bounds.


For users of Kafka Clients or Kafka Connect in environments that trust users with disk and environment variable access, it is not recommended to set the system property.
For users of the Kafka Broker, Kafka MirrorMaker 2.0, Kafka Streams, and Kafka command-line tools, it is not recommended to set the system property.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31141
- https://github.com/apache/kafka
- https://lists.apache.org/thread/9whdzfr0zwdhr364604w5ssnzmg4v2lv
- https://security.netapp.com/advisory/ntap-20250131-0001
- http://www.openwall.com/lists/oss-security/2024/11/18/5
