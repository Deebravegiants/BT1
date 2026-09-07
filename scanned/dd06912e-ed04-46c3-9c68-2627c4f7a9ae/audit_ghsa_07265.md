# [H] Netty: [Bzip2Decoder] Infinite Loop in RLE State Machine Leads to Event-Loop Thread Hang

## Summary
Severity: High
Advisory: GHSA-558v-64gr-wgg4
CVE: CVE-2026-59901
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-558v-64gr-wgg4
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-compression` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec` — affected >=0 <4.1.136.Final

## Details
The `Bzip2Decoder` handler in Netty's compression codec pipeline is vulnerable to a denial-of-service attack through a malformed bzip2 stream that permanently captures the event-loop thread in an infinite loop. The vulnerability exists in the run-length encoding (RLE) state machine within [`Bzip2BlockDecompressor.read()`]

## References
- https://github.com/netty/netty/security/advisories/GHSA-558v-64gr-wgg4
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
