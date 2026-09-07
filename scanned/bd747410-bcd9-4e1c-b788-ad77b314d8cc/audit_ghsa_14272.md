# [M] Lightbend Alpakka Kafka logs credentials on debug level

## Summary
Severity: Medium
Advisory: GHSA-55vq-xpjf-r2xc
CVE: CVE-2023-29471
CWE: CWE-312, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-55vq-xpjf-r2xc
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-stream-kafka_3` — affected >=0 <4.0.2
- Maven: `com.typesafe.akka:akka-stream-kafka_2.13` — affected >=0 <4.0.2
- Maven: `com.typesafe.akka:akka-stream-kafka_2.12` — affected >=0 <4.0.2
- Maven: `com.typesafe.akka:akka-stream-kafka_2.11` — affected >=0

## Details
Lightbend Alpakka Kafka before 4.0.2 logs its configuration as debug information, and thus log files may contain credentials (if plain cleartext login is configured). This occurs in akka.kafka.internal.KafkaConsumerActor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29471
- https://github.com/akka/alpakka-kafka/issues/1592
- https://github.com/akka/alpakka-kafka/pull/1614/commits/4011b704e93b22f6fd956aac516c7159d384644c
- https://akka.io/security/alpakka-kafka-cve-2023-29471.html
- https://github.com/akka/alpakka-kafka
