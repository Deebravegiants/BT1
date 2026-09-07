# [M] netty-incubator-codec-ohttp: Binary HTTP parser unchecked varint length overflow causes decoder crash

## Summary
Severity: Medium
Advisory: GHSA-pgrf-4654-3gq8
CVE: CVE-2026-61799
CWE: CWE-190, CWE-248, CWE-681
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-pgrf-4654-3gq8
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-bhttp` — affected >=0 <0.0.23.Final

## Details
## Summary

`io.netty.incubator:netty-incubator-codec-bhttp` uses attacker-controlled Binary HTTP variable-length integers as `long` values but accumulates them into `int` offsets. Large valid varint lengths wrap the internal offset negative, leading to unchecked `ArrayIndexOutOfBoundsException` / `IndexOutOfBoundsException` from a tiny malformed BHTTP payload. A remote peer can trigger connection-level denial of service in applications that expose `BinaryHttpParser` / `BinaryHttpDecoder` to untrusted input.

## Details

In `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java`, several parser paths store cumulative byte offsets in `int sumBytes` and then add attacker-controlled `long` lengths using compound assignment. In Java, `int += long` narrows the result back to `int`, so a length such as `2^31` wraps `sumBytes` negative.

Primary request-control-data path:

- `readRequestHead(...)` declares `int sumBytes = 0` at `BinaryHttpParser.java:386`.
- It reads `methodLength` as a `long` at `BinaryHttpParser.java:394`.
- It performs `sumBytes += methodLength` at `BinaryHttpParser.java:395`, narrowing the result to `int`.
- If `methodLength` is `2^31`, `sumBytes` wraps negative and bypasses `if (sumBytes >= in.readableBytes()) return null` at `BinaryHttpParser.java:396-398`.
- The parser then computes `schemeLengthIdx = in.readerIndex() + sumBytes` and calls `in.getByte(schemeLengthIdx)` at `BinaryHttpParser.java:401-402`, producing a negative index exception.

The same pattern is present in header parsing:

- `readFieldLine(...)` uses `int sumBytes` and adds `long nameLength` / `long valueLength` at `BinaryHttpParser.java:659-680`.
- `valueLengthIdx = nameIdx + (int) nameLength` at `BinaryHttpParser.java:674` can also overflow.

`getIndeterminateLength(...)` similarly uses `int sumBytes` and `long possibleTerminator` at `BinaryHttpParser.java:544-553`.

## Proof of concept

Safe local verification performed in this repository. After compiling `codec-bhttp`, the following minimal verifier uses a 15-byte payload:

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.incubator.codec.bhttp.BinaryHttpParser;

public final class VerifyBhttpOverflow {
  public static void main(String[] args) {
    byte[] payload = new byte[] {
      0x00, (byte)0xc0, 0x00, 0x00, 0x00, (byte)0x80, 0x00, 0x00, 0x00,
      0x47, 0x45, 0x54, 0x58, 0x58, 0x58
    };
    ByteBuf input = Unpooled.wrappedBuffer(payload);
    try {
      new BinaryHttpParser(8192).parse(input, false);
      System.out.println("returned");
    } catch (Throwable t) {
      System.out.println(t.getClass().getName());
      System.out.println(t.getMessage());
    }
  }
}
```

Payload interpretation:

- `00`: known-length request frame indicator.
- `c000000080000000`: valid 8-byte varint encoding of `0x80000000` (`2^31`) as the method length.
- `474554585858`: a few dummy bytes so the parser proceeds far enough to compute the next index.

Observed result:

```text
java.lang.ArrayIndexOutOfBoundsException
Index -2147483639 out of bounds for length 15
```

The parser should reject the malformed/incomplete message with a controlled decoder exception or return `null` awaiting more bytes; it should not allow integer wraparound to reach unchecked buffer indexing.

## Impact

A remote peer can trigger an unchecked exception in the Binary HTTP decoder using a tiny payload. In typical Netty pipelines this closes or fails the affected channel. Depending on application-level exception handling, repeated payloads can cause sustained denial of service for exposed BHTTP endpoints. No memory corruption or information disclosure was observed because the failure occurs in Java/Netty bounds checks.

## Suggested remediation

- Use `long` for all cumulative byte counts derived from protocol lengths.
- Before converting any protocol length to `int`, verify it is non-negative, no larger than `Integer.MAX_VALUE`, and no larger than available readable bytes and configured limits.
- Replace `sumBytes >= in.readableBytes()` checks with precise checked arithmetic that permits exact-boundary complete fields but rejects impossible lengths.
- Throw a controlled `CorruptedFrameException` / `TooLongFrameException` for invalid or unsupported lengths.
- Add regression tests for 8-byte varint lengths at and above `Integer.MAX_VALUE` in request control data, response control data, known and indeterminate field sections, and field lines.

## References

- `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:386-402`
- `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:659-680`
- `codec-bhttp/src/main/java/io/netty/incubator/codec/bhttp/BinaryHttpParser.java:544-553`
- RFC 9292: Binary Representation of HTTP Messages
- RFC 9000 variable-length integer encoding

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-pgrf-4654-3gq8
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/releases/tag/netty-incubator-codec-parent-ohttp-0.0.23.Final
