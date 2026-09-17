# [M] Netty: HttpObjectDecoder skips arbitrary initial control characters when only initial CRLF characters are permitted

## Summary
Severity: Medium
Advisory: GHSA-hvcg-qmg6-jm4c
CVE: CVE-2026-50020
CWE: CWE-444
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-hvcg-qmg6-jm4c
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-http` — affected >=0 <4.1.135.Final

## Details
## Summary

Before reading the first request-line, `HttpObjectDecoder` skips every byte for which
`Character.isISOControl(b)` is `true` (0x00–0x1F and 0x7F) as well as all whitespace.
RFC 9112 §2.2 only asks servers to ignore **empty CRLF lines** preceding the request-line —
a carefully scoped robustness allowance intended to handle HTTP/1.0 POST workarounds.
Silently absorbing NUL bytes, SOH, STX, and other non-CRLF control characters goes
significantly beyond this, and can be exploited for request-boundary confusion in pipelined
or multiplexed transports where a front-end component treats those bytes differently.

## Affected Code

| File | Lines | Role |
|------|-------|------|
| `codec-http/src/main/java/io/netty/handler/codec/http/HttpObjectDecoder.java` | 1298–1313 | `ISO_CONTROL_OR_WHITESPACE` static initialiser — marks all ISO control chars |
| `codec-http/src/main/java/io/netty/handler/codec/http/HttpObjectDecoder.java` | 1307–1313 | `SKIP_CONTROL_CHARS_BYTES` `ByteProcessor` — skips the entire set |
| `codec-http/src/main/java/io/netty/handler/codec/http/HttpObjectDecoder.java` | 1275–1289 | `LineParser.skipControlChars` — advances `readerIndex` past all matching bytes |

## Specification Analysis

### RFC 9112 §2.2 — Message Parsing

> In the interest of robustness, a server that is expecting to receive and parse a
> request-line **SHOULD ignore at least one empty line (CRLF)** received prior to the
> request-line.

> An HTTP/1.1 user agent **MUST NOT** preface or follow a request with an extra CRLF.

### Deviation

The RFC names a single permitted exception: an **empty line** (bare CRLF, i.e. the two-byte
sequence `\r\n`).  The `ISO_CONTROL_OR_WHITESPACE` table is initialised as:

```java
for (byte b = Byte.MIN_VALUE; b < Byte.MAX_VALUE; b++) {
    ISO_CONTROL_OR_WHITESPACE[128 + b] =
        Character.isISOControl(b) || isWhitespace(b);
}
```

`Character.isISOControl` returns `true` for `0x00`–`0x1F` and `0x7F`.  This includes NUL
(`0x00`), SOH (`0x01`), STX (`0x02`), BEL (`0x07`), DEL (`0x7F`), and every other non-CRLF
control character.  The `SKIP_CONTROL_CHARS` state runs this scan unconditionally before the
first `READ_INITIAL`, meaning any sequence of such bytes prepended to a request is silently
consumed.

A load balancer or TLS terminator that does not perform the same scan sees a different
message boundary than Netty does, which is the basis of a request-desync / smuggling attack.

## Suggested Unit Test

Add to `HttpRequestDecoderTest.java`.

```java
@Test
public void testNonCrlfControlBytesPrecedingRequestLineAreRejected() {
    // RFC 9112 §2.2: servers SHOULD ignore "at least one empty line (CRLF)" before the
    // request-line.  Non-CRLF control bytes are not part of this robustness allowance
    // and must not be silently swallowed.
    EmbeddedChannel channel = new EmbeddedChannel(new HttpRequestDecoder());

    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(0x00);   // NUL  — not an empty CRLF line
    buf.writeByte(0x01);   // SOH  — not an empty CRLF line
    buf.writeCharSequence(
            "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n",
            CharsetUtil.US_ASCII);

    channel.writeInbound(buf);
    HttpRequest req = channel.readInbound();

    // Current behaviour: NUL and SOH are in ISO_CONTROL_OR_WHITESPACE, so they are
    // silently skipped; the request decodes successfully and isFailure() == false.
    //
    // RFC-correct behaviour: only empty CRLF lines should be ignored; NUL/SOH must
    // cause a parse error — isFailure() == true.
    assertTrue(
            req.decoderResult().isFailure(),
            "Non-CRLF control bytes before the request-line must not be silently skipped " +
            "(RFC 9112 §2.2 allows only empty CRLF lines)");

    assertFalse(channel.finish());
}
```

**Current behaviour (unfixed):** `skipControlChars` advances past `0x00` and `0x01` because
both are in `ISO_CONTROL_OR_WHITESPACE`; the request parses normally, `isFailure()` is
`false` → test **fails**.

**Expected behaviour after fix:** only CRLF empty lines are tolerated; non-CRLF control
bytes produce an error, `isFailure()` is `true` → test **passes**.

## References
- https://github.com/netty/netty/security/advisories/GHSA-hvcg-qmg6-jm4c
- https://nvd.nist.gov/vuln/detail/CVE-2026-50020
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
