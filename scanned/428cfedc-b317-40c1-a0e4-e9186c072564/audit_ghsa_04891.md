# [H] Netty has Unbounded Direct Memory Consumption in its RedisDecoder

## Summary
Severity: High
Advisory: GHSA-6ghj-frrj-jjj3
CVE: CVE-2026-44890
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-6ghj-frrj-jjj3
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.135.Final

## Details
### Summary
An attacker can cause DoS by sending crafted Redis payloads across multiple connections without `\r\n`. This exhausts the server's direct memory pool (OutOfDirectMemoryError), preventing legitimate connections from being processed.

### Details
io.netty.handler.codec.redis.RedisDecoder decodes the length of bulk strings and array headers using the `decodeLength` method. This method reads bytes from the network until it encounters a `\n` character. However, it does not enforce any maximum length check while buffering the bytes if the `\n` character is not found. An attacker can exploit this by sending a continuous stream of digits (e.g., `$1111...`) without ever sending a `\n`.

To cause a true Denial of Service, an attacker must open multiple concurrent connections and distribute the unbounded payloads among them.

According to the RESP specification (https://redis.io/docs/latest/develop/reference/protocol-spec/), all parts of the protocol are strictly terminated with `\r\n`. Furthermore, the length prefix itself is an integer representation that must fit within standard numeric limits (e.g., a 64-bit signed integer). Therefore, a stream of digits exceeding these bounds without `\r\n` is a protocol violation and should be rejected immediately rather than buffered indefinitely.

### Impact
Denial of Service due to memory exhaustion. Any application using Netty's RedisDecoder to handle untrusted Redis traffic is vulnerable.

## References
- https://github.com/netty/netty/security/advisories/GHSA-6ghj-frrj-jjj3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44890
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
