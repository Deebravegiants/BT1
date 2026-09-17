# [H] Netty: Unbounded pre-allocation in RedisArrayAggregator from RESP array length

## Summary
Severity: High
Advisory: GHSA-5w86-c3rq-vjj7
CVE: CVE-2026-50011
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-5w86-c3rq-vjj7
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.135.Final

## Details
### Summary
RedisArrayAggregator pre-allocates ArrayList with initial capacity equal to the RESP array element count declared in an array header. That count is taken from the wire before the corresponding child messages exist. A small malicious header can claim a huge initial capacity.

### Details
The aggregator starts a new aggregation level when it receives an ArrayHeaderRedisMessage. For positive lengths it pushes AggregateState, whose constructor runs `new ArrayList<>(length)`. No configurable maximum is applied in this handler, and the peer does not need to supply the array elements for the backing array allocation to occur.

In the same pipeline, RedisDecoder enforces RedisConstants.REDIS_MESSAGE_MAX_LENGTH for bulk string lengths but does not apply that cap to array header lengths. Declared array sizes can therefore be extremely large while still passing decoding, and the aggregator immediately attempts Object[] reservation.

io.netty.handler.codec.redis.RedisDecoder#decodeLength
io.netty.handler.codec.redis.RedisArrayAggregator#decodeRedisArrayHeader

### Impact
Availability / resource exhaustion via unbounded pre-allocation from untrusted RESP array headers.

## References
- https://github.com/netty/netty/security/advisories/GHSA-5w86-c3rq-vjj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-50011
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
