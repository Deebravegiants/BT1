# [M] Apache Kafka: SCRAM authentication vulnerable to replay attacks when used without encryption

## Summary
Severity: Medium
Advisory: BIT-kafka-2024-56128
Aliases: CVE-2024-56128, GHSA-p7c9-8xx8-h74f
Ecosystem: Bitnami
Published: 2024-12-24
Source: https://osv.dev/vulnerability/BIT-kafka-2024-56128
Type: osv

## Affected
- Bitnami: `kafka` — affected >=0.10.2 <3.7.2

## Details
Incorrect Implementation of Authentication Algorithm in Apache Kafka's SCRAM implementation.

Issue Summary:
Apache Kafka's implementation of the Salted Challenge Response Authentication Mechanism (SCRAM) did not fully adhere to the requirements of RFC 5802 [1].
Specifically, as per RFC 5802, the server must verify that the nonce sent by the client in the second message matches the nonce sent by the server in its first message.
However, Kafka's SCRAM implementation did not perform this validation.

Impact:
This vulnerability is exploitable only when an attacker has plaintext access to the SCRAM authentication exchange. However, the usage of SCRAM over plaintext is strongly
discouraged as it is considered an insecure practice [2]. Apache Kafka recommends deploying SCRAM exclusively with TLS encryption to protect SCRAM exchanges from interception [3].
Deployments using SCRAM with TLS are not affected by this issue.

How to Detect If You Are Impacted:
If your deployment uses SCRAM authentication over plaintext communication channels (without TLS encryption), you are likely impacted.
To check if TLS is enabled, review your server.properties configuration file for listeners property. If you have SASL_PLAINTEXT in the listeners, then you are likely impacted.

Fix Details:
The issue has been addressed by introducing nonce verification in the final message of the SCRAM authentication exchange to ensure compliance with RFC 5802.

Affected Versions:
Apache Kafka versions 0.10.2.0 through 3.9.0, excluding the fixed versions below.

Fixed Versions:
3.9.0
3.8.1
3.7.2

Users are advised to upgrade to 3.7.2 or later to mitigate this issue.

Recommendations for Mitigation:
Users unable to upgrade to the fixed versions can mitigate the issue by:
- Using TLS with SCRAM Authentication:
Always deploy SCRAM over TLS to encrypt authentication exchanges and protect against interception.
- Considering Alternative Authentication Mechanisms:
Evaluate alternative authentication mechanisms, such as PLAIN, Kerberos or OAuth with TLS, which provide additional layers of security.

## References
- https://datatracker.ietf.org/doc/html/rfc5802
- https://datatracker.ietf.org/doc/html/rfc5802#section-9
- https://kafka.apache.org/documentation/#security_sasl_scram_security
- https://lists.apache.org/thread/84dh4so32lwn7wr6c5s9mwh381vx9wkw
- http://www.openwall.com/lists/oss-security/2024/12/18/3
- https://nvd.nist.gov/vuln/detail/CVE-2024-56128
