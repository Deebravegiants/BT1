# [M] Apache Kafka Client Arbitrary File Read and Server Side Request Forgery Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vgq5-3255-v292
CVE: CVE-2025-27817
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-vgq5-3255-v292
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=3.1.0 <3.9.1

## Details
A possible arbitrary file read and SSRF vulnerability has been identified in Apache Kafka Client. Apache Kafka Clients accept configuration data for setting the SASL/OAUTHBEARER connection with the brokers, including "sasl.oauthbearer.token.endpoint.url" and "sasl.oauthbearer.jwks.endpoint.url". Apache Kafka allows clients to read an arbitrary file and return the content in the error log, or sending requests to an unintended location. In applications where Apache Kafka Clients configurations can be specified by an untrusted party, attackers may use the "sasl.oauthbearer.token.endpoint.url" and "sasl.oauthbearer.jwks.endpoint.url" configuratin to read arbitrary contents of the disk and environment variables or make requests to an unintended location. In particular, this flaw may be used in Apache Kafka Connect to escalate from REST API access to filesystem/environment/URL access, which may be undesirable in certain environments, including SaaS products. 

Since Apache Kafka 3.9.1/4.0.0, we have added a system property ("-Dorg.apache.kafka.sasl.oauthbearer.allowed.urls") to set the allowed urls in SASL JAAS configuration. In 3.9.1, it accepts all urls by default for backward compatibility. However in 4.0.0 and newer, the default value is empty list and users have to set the allowed urls explicitly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27817
- https://github.com/apache/kafka
- https://kafka.apache.org/cve-list
- http://www.openwall.com/lists/oss-security/2025/06/09/1
