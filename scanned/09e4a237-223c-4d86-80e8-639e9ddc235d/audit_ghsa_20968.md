# [M] Apache Pulsar Broker, Proxy, and WebSocket Proxy vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-jvf3-mfxv-jcqr
CVE: CVE-2022-33682
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-jvf3-mfxv-jcqr
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
TLS hostname verification cannot be enabled in the Pulsar Broker's Java Client, the Pulsar Broker's Java Admin Client, the Pulsar WebSocket Proxy's Java Client, and the Pulsar Proxy's Admin Client leaving intra-cluster connections and geo-replication connections vulnerable to man in the middle attacks, which could leak credentials, configuration data, message data, and any other data sent by these clients. The vulnerability is for both the pulsar+ssl protocol and HTTPS. An attacker can only take advantage of this vulnerability by taking control of a machine 'between' the client and the server. The attacker must then actively manipulate traffic to perform the attack by providing the client with a cryptographically valid certificate for an unrelated host. This issue affects Apache Pulsar Broker, Proxy, and WebSocket Proxy versions 2.7.0 to 2.7.4; 2.8.0 to 2.8.3; 2.9.0 to 2.9.2; 2.10.0; 2.6.4 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33682
- https://lists.apache.org/thread/l0ynfl161qghwfcgbbl8ld9hzbl9t3yx
