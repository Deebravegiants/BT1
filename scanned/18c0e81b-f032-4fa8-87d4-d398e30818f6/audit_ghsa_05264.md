# [H] Netty HTTP/3 QPACK Blocked Streams Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-4grm-h2qv-h6w6
CVE: CVE-2026-48748
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-4grm-h2qv-h6w6
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http3` — affected >=4.2.0.Final <4.2.15.Final

## Details
### Summary
A memory exhaustion vulnerability in the Netty HTTP/3 codec allows the creation of an infinite number of blocked streams, which can cause OOM error.

### Details
The vulnerability exists in `io.netty.handler.codec.http3.QpackDecoder#shouldWaitForDynamicTableUpdates`:

If a client sends a header referencing a table entry that the server hasn't received yet, the server must pause that stream and wait for the missing entry to arrive. To prevent attackers from exhausting resources by intentionally sending missing references, Netty limits the number of streams that can be blocked at the same time.

However, the check is implemented as:

```java
if (blockedStreamsCount == maxBlockedStreams - 1) {
```

If the server enables QPACK dynamic tables (by setting `HTTP3_SETTINGS_QPACK_MAX_TABLE_CAPACITY` > 0) but does not explicitly configure `HTTP3_SETTINGS_QPACK_BLOCKED_STREAMS`, it defaults to 0.

When `maxBlockedStreams` is 0, the condition evaluates to `blockedStreamsCount == -1`. Since `blockedStreamsCount` starts at `0` and only increments, it never equals `-1`. This bypasses the limit, allowing an attacker to open an infinite number of streams that block indefinitely. Additionally, the `QpackDecoder` never removes unblocked streams from the `blockedStreams` map or decrements the counter, meaning the `ReadResumptionListener` for each blocked stream is kept in memory for the entire lifetime of the connection. This exhausts server memory and crashes the JVM.

### Impact
Denial of Service. Any server using `netty-codec-http3` with QPACK dynamic tables enabled and maxBlockedStreams defaulting to 0 is impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-4grm-h2qv-h6w6
- https://nvd.nist.gov/vuln/detail/CVE-2026-48748
- https://github.com/netty/netty/commit/75127cab731ee35068d1f0667bffa188bc332f5d
- https://access.redhat.com/security/cve/CVE-2026-48748
- https://bugzilla.redhat.com/show_bug.cgi?id=2488441
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48748.json
