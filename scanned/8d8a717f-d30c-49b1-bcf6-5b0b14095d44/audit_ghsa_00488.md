# [M] Moderate severity vulnerability that affects org.apache.qpid:apache-qpid-broker-j

## Summary
Severity: Medium
Advisory: GHSA-6w3v-66mj-2qm6
CVE: CVE-2018-1298
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-6w3v-66mj-2qm6
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:apache-qpid-broker-j` — affected >=7.0.0 <7.0.1

## Details
A Denial of Service vulnerability was found in Apache Qpid Broker-J 7.0.0 in functionality for authentication of connections for AMQP protocols 0-8, 0-9, 0-91 and 0-10 when PLAIN or XOAUTH2 SASL mechanism is used. The vulnerability allows unauthenticated attacker to crash the broker instance. AMQP 1.0 and HTTP connections are not affected. An authentication of incoming AMQP connections in Apache Qpid Broker-J is performed by special entities called "Authentication Providers". Each Authentication Provider can support several SASL mechanisms which are offered to the connecting clients as part of SASL negotiation process. The client chooses the most appropriate SASL mechanism for authentication. Authentication Providers of following types supports PLAIN SASL mechanism: Plain, PlainPasswordFile, SimpleLDAP, Base64MD5PasswordFile, MD5, SCRAM-SHA-256, SCRAM-SHA-1. XOAUTH2 SASL mechanism is supported by Authentication Providers of type OAuth2. If an AMQP port is configured with any of these Authentication Providers, the Broker may be vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1298
- https://github.com/advisories/GHSA-6w3v-66mj-2qm6
- https://lists.apache.org/thread.html/d9087e9e57c9b6376754e2b4ea8cd5e9ae6449ed17fc384640c9c9e1@%3Cusers.qpid.apache.org%3E
