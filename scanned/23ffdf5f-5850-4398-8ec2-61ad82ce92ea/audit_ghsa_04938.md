# [H] Netty: Memory Exhaustion in RedisArrayAggregator due to Deeply Nested Arrays

## Summary
Severity: High
Advisory: GHSA-3244-j874-rhc2
CVE: CVE-2026-44250
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-3244-j874-rhc2
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.135.Final

## Details
### Summary
An attacker can cause DoS by sending a crafted Redis payload with deeply nested arrays. This forces the server to allocate a massive number of state objects and collections, leading to memory exhaustion and an OutOfMemoryError.

### Details
io.netty.handler.codec.redis.RedisArrayAggregator aggregates RedisMessage parts into ArrayRedisMessage. It uses a `Deque<AggregateState>` to keep track of nested arrays. However, it does not limit the maximum depth of nested arrays. When an attacker sends a continuous stream of nested array headers (e.g., `*1\r\n*1\r\n*1\r\n...`), RedisArrayAggregator pushes a `new AggregateState` onto the stack and allocates a `new ArrayList` for each header. Because there is no depth limit, an attacker can send millions of such headers. This consumes a massive amount of heap memory for the AggregateState instances and their backing ArrayLists, eventually resulting in an OutOfMemoryError.

### Impact
Denial of Service due to memory exhaustion. Any application using Netty's RedisArrayAggregator to handle untrusted Redis traffic is vulnerable.

## References
- https://github.com/netty/netty/security/advisories/GHSA-3244-j874-rhc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44250
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
