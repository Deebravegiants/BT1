# [M] RabbitMQ Java client: TrustEverythingTrustManager used by default in useSslProtocol() enables MITM

## Summary
Severity: Medium
Advisory: GHSA-5m9f-rphj-c435
CVE: CVE-2026-63336
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-5m9f-rphj-c435
Type: github-advisory

## Affected
- Maven: `com.rabbitmq:amqp-client` — affected >=0 <5.33.0

## Details
## Vulnerability Summary

`com.rabbitmq.client.TrustEverythingTrustManager` accepts ANY TLS certificate (including null chains) and is used as the default trust manager when calling `ConnectionFactory.useSslProtocol()` without arguments. Combined with hostname verification being disabled by default, this enables trivial man-in-the-middle attacks.

## Affected Components

- `com.rabbitmq.client.TrustEverythingTrustManager` — accepts any certificate
- `com.rabbitmq.client.ConnectionFactory.useSslProtocol()` — uses TrustEverythingTrustManager
- Hostname verification disabled by default (`enableHostnameVerification()` must be called explicitly)
- `com.rabbitmq.client.ConnectionFactory.getPassword()` — returns plaintext with no redaction
- Default port 5672 (plaintext) with PLAIN SASL — credentials sent unencrypted

## POC (Verified on Java 21, amqp-client 5.25.0)

```java
// TrustEverythingTrustManager accepts ANY certificate including null
TrustEverythingTrustManager tm = new TrustEverythingTrustManager();
tm.checkServerTrusted(null, "RSA");  // No exception — accepts null cert chain
tm.getAcceptedIssuers();  // Returns empty array — trusts all CAs

// ConnectionFactory defaults
ConnectionFactory factory = new ConnectionFactory();
factory.useSslProtocol();  // Uses TrustEverythingTrustManager internally
// enableHostnameVerification() NOT called by default

// Credential exposure
factory.setPassword("secret_password_123");
factory.getPassword();  // Returns "secret_password_123" — no redaction

// Default plaintext port
factory.getPort();  // 5672 (plaintext, not 5671/TLS)

// PLAIN SASL sends cleartext credentials
PlainMechanism pm = new PlainMechanism();
// handleChallenge() sends username+password in cleartext
```

## Attack Scenarios

1. **MITM**: Attacker presents self-signed cert → `TrustEverythingTrustManager` accepts it → all RabbitMQ traffic intercepted
2. **Credential theft**: Default plaintext port (5672) + PLAIN SASL = credentials readable on network
3. **DNS rebinding**: No hostname verification → attacker DNS record → MITM without cert
4. **Logging exposure**: `getPassword()` returns plaintext → credentials in logs/stack traces

## Suggested Fix
1. Deprecate `TrustEverythingTrustManager` — it should never be used in production
2. `useSslProtocol()` should use the JVM default trust store, not TrustEverything
3. Enable hostname verification by default
4. Redact password in `getPassword()` or remove the public getter
5. Warn when using PLAIN SASL without TLS

## References
- https://github.com/rabbitmq/rabbitmq-java-client/security/advisories/GHSA-5m9f-rphj-c435
- https://github.com/rabbitmq/rabbitmq-java-client/pull/1999
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2001
- https://github.com/rabbitmq/rabbitmq-java-client/commit/1e7deb2e6020c9793a81385a53ea378ec63b9339
- https://github.com/rabbitmq/rabbitmq-java-client/commit/a4bf571dd368765baaa9cecfae68ce09f1bdcc01
- https://github.com/rabbitmq/rabbitmq-java-client
- https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.33.0
