# [H] Netty HAProxy: Unbalanced Reference Count in Nested PP2_TYPE_SSL TLV Parsing Leads to Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-h2qv-fj59-j46j
CVE: CVE-2026-48059
CWE: CWE-1286, CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-h2qv-fj59-j46j
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-haproxy` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-haproxy` — affected >=0 <4.1.135.Final

## Details
### Impact
The HAProxy PROXY protocol v2 codec in netty leaks native or heap memory on every connection when a client sends a syntactically valid header containing nested `PP2_TYPE_SSL` TLVs (type-length-value records) at depth two or greater. The leak occurs on the successful parse path — no exception is thrown, the message fires downstream, the decoder removes itself, and the application releases the `HAProxyMessage` normally. Yet the underlying cumulation buffer (a pooled, potentially direct `ByteBuf` allocated by the channel) remains permanently pinned.

## References
- https://github.com/netty/netty/security/advisories/GHSA-h2qv-fj59-j46j
- https://nvd.nist.gov/vuln/detail/CVE-2026-48059
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48059.json
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty
- https://bugzilla.redhat.com/show_bug.cgi?id=2488437
- https://access.redhat.com/security/cve/CVE-2026-48059
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:53806
- https://access.redhat.com/errata/RHSA-2026:53644
- https://access.redhat.com/errata/RHSA-2026:50085
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:41951
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/errata/RHSA-2026:36820
- https://access.redhat.com/errata/RHSA-2026:34608
- https://access.redhat.com/errata/RHSA-2026:26586
- https://access.redhat.com/errata/RHSA-2026:26018
- https://access.redhat.com/errata/RHSA-2026:26017
