# [H] Apache Kafka Clients: Kafka Producer Message Corruption and Misrouting via Buffer Pool Race Condition

## Summary
Severity: High
Advisory: GHSA-5qcv-4rpc-jp93
CVE: CVE-2026-35554
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-5qcv-4rpc-jp93
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=2.8.0 <3.9.2
- Maven: `org.apache.kafka:kafka-clients` — affected >=4.0.0 <4.0.2
- Maven: `org.apache.kafka:kafka-clients` — affected >=4.1.0 <4.1.2

## Details
A race condition in the Apache Kafka Java producer client’s buffer pool management can cause messages to be silently delivered to incorrect topics.

When a produce batch expires due to delivery.timeout.ms while a network request containing that batch is still in flight, the batch’s ByteBuffer is prematurely deallocated and returned to the buffer pool. If a subsequent producer batch—potentially destined for a different topic—reuses this freed buffer before the original network request completes, the buffer contents may become corrupted. This can result in messages being delivered to unintended topics without any error being reported to the producer.


Data Confidentiality:
Messages intended for one topic may be delivered to a different topic, potentially exposing sensitive data to consumers who have access to the destination topic but not the intended source topic.

Data Integrity:
Consumers on the receiving topic may encounter unexpected or incompatible messages, leading to deserialization failures, processing errors, and corrupted downstream data.

This issue affects Apache Kafka versions ≤ 3.9.1, ≤ 4.0.1, and  ≤ 4.1.1.

Kafka users are advised to upgrade to 3.9.2, 4.0.2, 4.1.2, 4.2.0, or later to address this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35554
- https://github.com/apache/kafka/pull/21065
- https://github.com/apache/kafka/pull/21285
- https://github.com/apache/kafka/pull/21286
- https://github.com/apache/kafka/pull/21287
- https://github.com/apache/kafka/pull/21288
- https://github.com/apache/kafka/commit/1df2ac5b2ba4d1b5ed54b895ff6fb9539303ccb5
- https://github.com/apache/kafka
- https://issues.apache.org/jira/browse/KAFKA-19012
- https://lists.apache.org/thread/f07x7j8ovyqhjd1to25jsnqbm6wj01d6
- http://www.openwall.com/lists/oss-security/2026/04/07/6
