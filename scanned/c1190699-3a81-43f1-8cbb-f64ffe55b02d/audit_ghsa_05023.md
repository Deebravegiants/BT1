# [H] Netty's Lack of Lifecycle Cleanup Leads to Pooled ByteBuf Leak in RedisArrayAggregator

## Summary
Severity: High
Advisory: GHSA-6jv9-x5w9-2ccm
CVE: CVE-2026-48006
CWE: CWE-401, CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6jv9-x5w9-2ccm
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-redis` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-redis` — affected >=0 <4.1.135.Final

## Details
### Impact
The RedisArrayAggregator handler permanently leaks pooled direct-memory buffers when a Redis pipeline connection closes before a RESP array aggregate completes. The handler retains child messages in per-handler state (`depths` field) but defines no `channelInactive`, `handlerRemoved`, or `exceptionCaught` method to release them when the pipeline tears down. Because the leaked buffers are slices of `PooledByteBufAllocator` chunks, they prevent those chunks from being returned to the JVM-wide direct-memory pool. Repeated connection churn by any network peer monotonically drains this shared pool, eventually causing allocation failures on all Netty channels in the process.

## References
- https://github.com/netty/netty/security/advisories/GHSA-6jv9-x5w9-2ccm
- https://nvd.nist.gov/vuln/detail/CVE-2026-48006
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:50085
- https://access.redhat.com/errata/RHSA-2026:53644
- https://access.redhat.com/errata/RHSA-2026:53806
- https://access.redhat.com/security/cve/CVE-2026-48006
- https://bugzilla.redhat.com/show_bug.cgi?id=2488433
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48006.json
