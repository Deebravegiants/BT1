# [H] Apache Pulsar SASL Authentication Provider observable timing discrepancy vulnerability

## Summary
Severity: High
Advisory: GHSA-c57v-4vg5-cm2x
CVE: CVE-2023-51437
CWE: CWE-200, CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-07
Source: https://github.com/advisories/GHSA-c57v-4vg5-cm2x
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-broker-auth-sasl` — affected >=0 <2.11.3
- Maven: `org.apache.pulsar:pulsar-broker-auth-sasl` — affected >=3.0.0 <3.0.2
- Maven: `org.apache.pulsar:pulsar-broker-auth-sasl` — affected >=3.1.0 <3.1.1

## Details
Observable timing discrepancy vulnerability in Apache Pulsar SASL Authentication Provider can allow an attacker to forge a SASL Role Token that will pass signature verification.
Users are recommended to upgrade to version 2.11.3, 3.0.2, or 3.1.1 which fixes the issue. Users should also consider updating the configured secret in the `saslJaasServerRoleTokenSignerSecretPath` file.

Any component matching an above version running the SASL Authentication Provider is affected. That includes the Pulsar Broker, Proxy, Websocket Proxy, or Function Worker.

2.11 Pulsar users should upgrade to at least 2.11.3.
3.0 Pulsar users should upgrade to at least 3.0.2.
3.1 Pulsar users should upgrade to at least 3.1.1.
Any users running Pulsar 2.8, 2.9, 2.10, and earlier should upgrade to one of the above patched versions.

For additional details on this attack vector, please refer to  https://codahale.com/a-lesson-in-timing-attacks/ .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51437
- https://github.com/apache/pulsar/pull/21061
- https://github.com/apache/pulsar/commit/6274fa01a75d74d559bb7e514c970f1fc07d15bc
- https://github.com/apache/pulsar/commit/bc1019fa8ed37b8a4c8bb01e3662c6c015e1bc27
- https://github.com/apache/pulsar/commit/c05954e66ff33098aeb848f4bde51613ace7e47e
- https://github.com/apache/pulsar/commit/c27beca64cc93848c40a374f19eaf4d3cc4f4f03
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/5kgmvvolf5tzp5rz9xjwfg2ncwvqqgl5
- https://www.openwall.com/lists/oss-security/2024/02/07/1
- http://www.openwall.com/lists/oss-security/2024/02/07/1
