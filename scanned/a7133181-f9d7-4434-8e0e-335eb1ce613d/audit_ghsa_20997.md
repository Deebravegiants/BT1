# [M] Apache Pulsar Brokers and Proxies vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-j3qw-g67q-7m64
CVE: CVE-2022-33683
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-j3qw-g67q-7m64
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=0 <2.7.5
- Maven: `org.apache.pulsar:pulsar-proxy` — affected >=0 <2.7.5
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.8.0 <2.8.4
- Maven: `org.apache.pulsar:pulsar-proxy` — affected >=2.8.0 <2.8.4
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.9.0 <2.9.3
- Maven: `org.apache.pulsar:pulsar-proxy` — affected >=2.9.0 <2.9.3
- Maven: `org.apache.pulsar:pulsar-broker` — affected >=2.10.0 <2.10.1
- Maven: `org.apache.pulsar:pulsar-proxy` — affected >=2.10.0 <2.10.1

## Details
Apache Pulsar Brokers and Proxies create an internal Pulsar Admin Client that does not verify peer TLS certificates, even when tlsAllowInsecureConnection is disabled via configuration. The Pulsar Admin Client's intra-cluster and geo-replication HTTPS connections are vulnerable to man in the middle attacks, which could leak authentication data, configuration data, and any other data sent by these clients. An attacker can only take advantage of this vulnerability by taking control of a machine 'between' the client and the server. The attacker must then actively manipulate traffic to perform the attack. This issue affects Apache Pulsar Broker and Proxy versions 2.7.0 to 2.7.4; 2.8.0 to 2.8.3; 2.9.0 to 2.9.2; 2.10.0; 2.6.4 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33683
- https://lists.apache.org/thread/42v5rsxj36r3nhfxhmhb2x12r5jmvx3x
