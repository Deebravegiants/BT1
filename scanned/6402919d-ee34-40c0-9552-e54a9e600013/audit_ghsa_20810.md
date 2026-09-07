# [M] Apache Pulsar Java Client vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-c5fp-x2h5-vjv7
CVE: CVE-2022-33681
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-25
Source: https://github.com/advisories/GHSA-c5fp-x2h5-vjv7
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-client` — affected >=0 <2.7.5
- Maven: `org.apache.pulsar:pulsar-client` — affected >=2.8.0 <2.8.4
- Maven: `org.apache.pulsar:pulsar-client` — affected >=2.9.0 <2.9.3
- Maven: `org.apache.pulsar:pulsar-client` — affected >=2.10.0 <2.10.1

## Details
Delayed TLS hostname verification in the Pulsar Java Client and the Pulsar Proxy make each client vulnerable to a man in the middle attack. Connections from the Pulsar Java Client to the Pulsar Broker/Proxy and connections from the Pulsar Proxy to the Pulsar Broker are vulnerable. Authentication data is sent before verifying the server’s TLS certificate matches the hostname, which means authentication data could be exposed to an attacker. An attacker can only take advantage of this vulnerability by taking control of a machine 'between' the client and the server. The attacker must then actively manipulate traffic to perform the attack by providing the client with a cryptographically valid certificate for an unrelated host. Because the client sends authentication data before performing hostname verification, an attacker could gain access to the client’s authentication data. The client eventually closes the connection when it verifies the hostname and identifies the targeted hostname does not match a hostname on the certificate. Because the client eventually closes the connection, the value of the intercepted authentication data depends on the authentication method used by the client. Token based authentication and username/password authentication methods are vulnerable because the authentication data can be used to impersonate the client in a separate session. This issue affects Apache Pulsar Java Client versions 2.7.0 to 2.7.4; 2.8.0 to 2.8.3; 2.9.0 to 2.9.2; 2.10.0; 2.6.4 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33681
- https://github.com/apache/pulsar/tree/db26073728bf86fc80deecaece2dc02b50bbb9b5/pulsar-client
- https://lists.apache.org/thread/fpo6x10trvn20hlk0dmnr5vlz5v4kl3d
