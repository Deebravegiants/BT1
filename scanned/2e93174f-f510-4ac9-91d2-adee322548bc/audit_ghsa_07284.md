# [M] Netty: Memory Leak in DNS Record Decoder via Malformed Domain Names

## Summary
Severity: Medium
Advisory: GHSA-mfg7-5gfp-c4w3
CVE: CVE-2026-73508
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-mfg7-5gfp-c4w3
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-dns` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-dns` — affected >=0 <4.1.136.Final

## Details
### Summary
A memory leak can be caused in Netty's DNS codec by sending malicious DNS packets containing invalid domain names. Because the leak occurs incrementally per packet, sustained malicious requests will cause a gradual Denial of Service.

### Details
Inside `io.netty.handler.codec.dns.AbstractDnsRecord`, the parsed domain name string is passed to `IDN.toASCII(name)`. If the domain name contains characters that violate IDNA rules, `IDN.toASCII` throws an `IllegalArgumentException`.

Because this exception occurs inside the constructor before the `DnsRecord` instance can assign the buffer to its content field for later release, the ByteBuf whose reference count was incremented (or newly allocated) is never released, resulting in a direct memory leak.

There are several places where variants of this leak happen:
- `io.netty.handler.codec.dns.DefaultDnsRecordDecoder#decodeRecord(java.lang.String, io.netty.handler.codec.dns.DnsRecordType, int, long, io.netty.buffer.ByteBuf, int, int)` invokes `in.retainedDuplicate()` or creates a new buffer `out` when constructing `DefaultDnsRawRecord`
- `io.netty.handler.codec.dns.DnsCodecUtil#decompressDomainName` allocates a new `ByteBuf` and passes it to `encodeDomainName()`. If the decompressed domain name contains a null byte (`\0`), `encodeDomainName()` throws an `IllegalArgumentException`, leaking the newly allocated buffer.

### Impact
Resource Exhaustion. Any application utilizing Netty's DnsRecordDecoder (such as DnsNameResolver or custom DNS servers) is vulnerable.

## References
- https://github.com/netty/netty/security/advisories/GHSA-mfg7-5gfp-c4w3
- https://github.com/netty/netty/pull/17063
- https://github.com/netty/netty/pull/17065
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
