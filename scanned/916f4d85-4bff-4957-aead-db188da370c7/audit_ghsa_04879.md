# [H] Netty: HAProxy SSL TLV parsing leaks retained slice on invalid TLV length

## Summary
Severity: High
Advisory: GHSA-cc37-9q2j-3hfv
CVE: CVE-2026-44893
CWE: CWE-703
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-cc37-9q2j-3hfv
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-haproxy` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-haproxy` — affected >=0 <4.1.135.Final

## Details
When decoding a PP2_TYPE_SSL TLV, HAProxyMessage.readNextTLV() first calls `header.retainedSlice(header.readerIndex(), length)` and only then reads the 1-byte client field and 4-byte verify field. If the attacker sets the TLV length below 5, the subsequent readByte/readInt throws IndexOutOfBoundsException. HAProxyMessageDecoder only catches HAProxyProtocolException around this call, so the IOOBE propagates and the retained slice on the pooled cumulation buffer is never released.

## References
- https://github.com/netty/netty/security/advisories/GHSA-cc37-9q2j-3hfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44893
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
