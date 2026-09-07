# [H] RabbitMQ Java client ValueReader: Oversized LongString/bytes length triggers OOM via unchecked allocation

## Summary
Severity: High
Advisory: GHSA-68mj-5wr7-6fgg
CVE: CVE-2026-69219
CWE: CWE-789
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-68mj-5wr7-6fgg
Type: github-advisory

## Affected
- Maven: `com.rabbitmq:amqp-client` — affected >=0 <5.33.1

## Details
## Summary

`ValueReader.readBytes()` allocates a byte array sized by a wire-declared content length without validating it against actual frame data. A malicious AMQP peer triggers OOM by declaring a ~2GB string/bytes field.

## Vulnerable Code

`src/main/java/com/rabbitmq/client/impl/ValueReader.java` lines 83-95:

```java
private static byte[] readBytes(final DataInputStream in) throws IOException {
    final long contentLength = unsignedExtend(in.readInt());
    if(contentLength < Integer.MAX_VALUE) {
        final byte[] buffer = new byte[(int)contentLength];  // allocates before reading
        in.readFully(buffer);
        return buffer;
    }
}
```

## Attack Scenario

A malicious AMQP server sends a LongString field (type tag 'S') with declared length `0x7FFFFFFE` (2,147,483,646). The check `contentLength < Integer.MAX_VALUE` passes. `new byte[2147483646]` attempts ~2GB allocation, causing `OutOfMemoryError` before `readFully()` attempts to read data.

The allocation size is attacker-controlled and is NOT validated against the frame size or `TruncatedInputStream` bounds. Exploitable pre-authentication via `connection.start` server-properties table.

## Impact

Denial of service via JVM `OutOfMemoryError`. Crashes the entire JVM.

## CWE

CWE-789: Memory Allocation with Excessive Size Value

## Remediation

Validate `contentLength` against the frame's remaining bytes or the negotiated max frame size (default 131,072) before allocating.

## References
- https://github.com/rabbitmq/rabbitmq-java-client/security/advisories/GHSA-68mj-5wr7-6fgg
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2007
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2008
- https://github.com/rabbitmq/rabbitmq-java-client/commit/388209356c6478088efce4d8a07b68e73837a7a0
- https://github.com/rabbitmq/rabbitmq-java-client/commit/6a87a8dcdc8b4cc4b961a7cdd388276446e5dfb2
- https://github.com/rabbitmq/rabbitmq-java-client
- https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.33.1
