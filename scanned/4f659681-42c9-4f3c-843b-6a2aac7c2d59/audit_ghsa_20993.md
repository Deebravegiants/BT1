# [H] Apache Kafka vulnerability can lead to brokers hitting OutOfMemoryException, causing Denial of Service

## Summary
Severity: High
Advisory: GHSA-c9h3-c6qj-hh7q
CVE: CVE-2022-34917
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-c9h3-c6qj-hh7q
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka` — affected >=2.8.0 <2.8.2
- Maven: `org.apache.kafka:kafka` — affected >=3.0.0 <3.0.2
- Maven: `org.apache.kafka:kafka` — affected >=3.1.0 <3.1.2
- Maven: `org.apache.kafka:kafka` — affected >=3.2.0 <3.2.3

## Details
A security vulnerability has been identified in Apache Kafka. It affects all releases since 2.8.0. The vulnerability allows malicious unauthenticated clients to allocate large amounts of memory on brokers. This can lead to brokers hitting OutOfMemoryException and causing denial of service. Example scenarios: - Kafka cluster without authentication: Any clients able to establish a network connection to a broker can trigger the issue. - Kafka cluster with SASL authentication: Any clients able to establish a network connection to a broker, without the need for valid SASL credentials, can trigger the issue. - Kafka cluster with TLS authentication: Only clients able to successfully authenticate via TLS can trigger the issue. We advise the users to upgrade the Kafka installations to one of the 3.2.3, 3.1.2, 3.0.2, 2.8.2 versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34917
- https://github.com/apache/kafka/commit/14951a83e3fdead212156e5532359500d72f68bc
- https://github.com/apache/kafka/commit/2bfa24b2bd416e7b8c4a0c566b984c43904fdecb
- https://github.com/apache/kafka/commit/aaceb6b79bfcb1d32874ccdbc8f3138d1c1c00fb
- https://github.com/apache/kafka/commit/c1295662768e64b4467e27c3d5158f95f2307657
- https://issues.apache.org/jira/browse/KAFKA-14063
- https://kafka.apache.org/cve-list
- https://kafka.apache.org/cve-list#CVE-2022-34917
