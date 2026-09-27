# [H] Strimzi allows unrestricted access to all Secrets in the same Kubernetes namespace from Kafka Connect and MirrorMaker 2 operands

## Summary
Severity: High
Advisory: GHSA-xrhh-hx36-485q
CVE: CVE-2025-66623
CWE: CWE-200, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-xrhh-hx36-485q
Type: github-advisory

## Affected
- Maven: `io.strimzi:strimzi` — affected >=0.47.0 <0.49.1

## Details
### Impact

In some situations, Strimzi creates an incorrect Kubernetes `Role` which grants the Apache Kafka Connect and Apache Kafka MirrorMaker 2 operands the `GET` access to all Kubernetes Secrets that exist in the given Kubernetes namespace. The exact scenario when this happens is when:
* Apache Kafka Connect is deployed without at least one of the following options configured:
    * TLS encryption with configured trusted certificates (no `.spec.tls.trustedCertificates` section in the `KafkaConnect` CR)
    * mTLS authentication (no `type: tls` in `.spec.authentication` section of the `KafkaConnect` CR)
    * TLS encryption with configured trusted certificates for `type: oauth` authentication (no `.spec.authentication.tlsTrustedCertificates` section in the `KafkaConnect` CR)
* Apache Kafka MirrorMaker2 is deployed without at least one of the following options configured for the target cluster:
    * TLS encryption with configured trusted certificates (no `.spec.target.tls.trustedCertificates` section in the `KafkaConnect` CR)
    * mTLS authentication (no `type: tls` in `.spec.target.authentication` section of the `KafkaConnect` CR)
    * TLS encryption with configured trusted certificates for `type: oauth` authentication (no `.spec.target.authentication.tlsTrustedCertificates` section in the `KafkaConnect` CR)
    * TLS encryption with configured trusted certificates (no `.spec.clusters[].tls.trustedCertificates` section in the `KafkaConnect` CR for the target cluster)
    * mTLS authentication (no `type: tls` in `.spec.clusters[].authentication` section of the `KafkaConnect` CR for the target cluster)
    * TLS encryption with configured trusted certificates for `type: oauth` authentication (no `.spec.clusters[].authentication.tlsTrustedCertificates` section in the `KafkaConnect` CR for the target cluster)

When the operands configured as described above are deployed with Strimzi >= 0.47.0 and <= 0.49.0, any code running within their Pods and using their Service Account for authentication will be able to `GET` any Kubernetes Secret from the same namespace. This can be done by executing 3rd party tools from the Pods. Or directly from the Kafka Connect code, for example, using configuration providers or HTTP connectors. The Pods are allowed to only `GET` the Secrets. They are not allowed to list, watch, modify, or delete the Secrets.

### Patches

The issue is fixed in Strimzi 0.49.1.

### Workarounds

There is no workaround for this issue when using the affected operands with the affected configurations.

## References
- https://github.com/strimzi/strimzi-kafka-operator/security/advisories/GHSA-xrhh-hx36-485q
- https://nvd.nist.gov/vuln/detail/CVE-2025-66623
- https://github.com/strimzi/strimzi-kafka-operator/commit/c8a14935e99c91eb0dd865431f46515da9f82ccc
- https://github.com/strimzi/strimzi-kafka-operator
