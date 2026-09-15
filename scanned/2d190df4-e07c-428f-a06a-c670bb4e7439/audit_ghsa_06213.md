# [H] RabbitMQ Java client ValueReader: Unbounded recursive table/array nesting causes StackOverflowError DoS

## Summary
Severity: High
Advisory: GHSA-93j5-89vc-pph4
CVE: CVE-2026-69220
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-93j5-89vc-pph4
Type: github-advisory

## Affected
- Maven: `com.rabbitmq:amqp-client` — affected >=0 <5.33.1

## Details
## Summary

`ValueReader.readTable()` and `readArray()` recursively call `readFieldValue()` with no depth limit. A malicious AMQP peer can crash the client JVM by sending a deeply nested table structure.

## Vulnerable Code

`src/main/java/com/rabbitmq/client/impl/ValueReader.java` lines 139-155 and 237-249:

```java
private static Map<String, Object> readTable(DataInputStream in) throws IOException {
    long tableLength = unsignedExtend(in.readInt());
    // ...
    while(tableIn.available() > 0) {
        String name = readShortstr(tableIn);
        Object value = readFieldValue(tableIn);  // recursive call
    }
}

static Object readFieldValue(DataInputStream in) throws IOException {
    switch(in.readUnsignedByte()) {
      case 'F': value = readTable(in);  // mutual recursion
      case 'A': value = readArray(in);  // mutual recursion
    }
}
```

## Attack Scenario

A malicious AMQP server (or MitM) sends a `connection.start` frame with ~580 levels of nested tables. Each level costs ~7 bytes (4-byte length + 1-byte key length + 1-byte key + 1-byte type tag), totaling ~4060 bytes within the 131,072 byte max frame size. With the default JVM stack (~512KB, ~864 bytes/frame), this triggers `StackOverflowError`, killing the I/O thread.

Exploitable pre-authentication since `connection.start` is the very first server frame.

## Impact

Denial of service. `StackOverflowError` kills the client I/O thread.

## CWE

CWE-674: Uncontrolled Recursion

## Remediation

Add a depth counter to `readTable`/`readArray`/`readFieldValue` and throw `MalformedFrameException` when exceeding a threshold (e.g., 32).

## References
- https://github.com/rabbitmq/rabbitmq-java-client/security/advisories/GHSA-93j5-89vc-pph4
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2007
- https://github.com/rabbitmq/rabbitmq-java-client/pull/2008
- https://github.com/rabbitmq/rabbitmq-java-client/commit/09af76fce136f3136931654a0a1d43095c80e2f0
- https://github.com/rabbitmq/rabbitmq-java-client/commit/db89e34809fbc6ba4e946615f297f3684ccd0acc
- https://github.com/rabbitmq/rabbitmq-java-client
- https://github.com/rabbitmq/rabbitmq-java-client/releases/tag/v5.33.1
