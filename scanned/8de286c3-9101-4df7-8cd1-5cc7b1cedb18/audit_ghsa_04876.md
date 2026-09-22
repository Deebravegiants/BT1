# [M] netty-codec-http2: ByteBuf Reference-Count Leak in DelegatingDecompressorFrameListener Leads to Memory Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-c2gf-v879-257j
CVE: CVE-2026-48043
CWE: CWE-400, CWE-401, CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-c2gf-v879-257j
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.135.Final
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Alpha1 <4.2.15.Final

## Details
### Impact

The `DelegatingDecompressorFrameListener` class orchestrates HTTP/2 decompression by embedding a per-stream `EmbeddedChannel` that runs the appropriate decompression codec (gzip, deflate, zstd) and forwards decompressed chunks to a wrapped listener. Each decompressed chunk is a pooled `ByteBuf` handed to an anonymous `ChannelInboundHandlerAdapter` tail handler, which becomes the sole owner responsible for releasing it.

A remote peer could send frames that would result in the flow-controller throwing and so trigger a resource leak which at the end might take down the whole JVM due OOME.

## References
- https://github.com/netty/netty/security/advisories/GHSA-c2gf-v879-257j
- https://nvd.nist.gov/vuln/detail/CVE-2026-48043
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48043.json
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty
- https://bugzilla.redhat.com/show_bug.cgi?id=2488442
- https://access.redhat.com/security/cve/CVE-2026-48043
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:53806
- https://access.redhat.com/errata/RHSA-2026:53644
- https://access.redhat.com/errata/RHSA-2026:50085
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:48124
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:34608
- https://access.redhat.com/errata/RHSA-2026:26586
- https://access.redhat.com/errata/RHSA-2026:26018
