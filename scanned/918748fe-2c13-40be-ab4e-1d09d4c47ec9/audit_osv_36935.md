# [M] Strimzi All CAs from CA chain will be trusted in Kafka Connect and Kafka MirrorMaker 2 target clusters

## Summary
Severity: Medium
Advisory: CVE-2026-27133
Aliases: GHSA-6x85-j2f7-4xc5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-27133
Type: osv

## Details
Strimzi provides a way to run an Apache Kafka cluster on Kubernetes or OpenShift in various deployment configurations. From 0.47.0 to before 0.50.1, when a chain consisting of multiple CA (Certificate Authority) certificates is used in the trusted certificates configuration of a Kafka Connect operand or of the target cluster in the Kafka MirrorMaker 2 operand, all of the certificates that are part of the CA chain will be trusted individually when connecting to the Apache Kafka cluster. Due to this error, the affected operand (Kafka Connect or Kafka MirrorMaker 2) might accept connections to Kafka brokers using server certificates signed by one of the other CAs in the CA chain and not just by the last CA in the chain. This issue is fixed in Strimzi 0.50.1.

## References
- https://github.com/strimzi/strimzi-kafka-operator/releases/tag/0.50.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27133.json
- https://github.com/strimzi/strimzi-kafka-operator/security/advisories/GHSA-6x85-j2f7-4xc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27133
