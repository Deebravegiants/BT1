# [H] Netty has a Vulnerable Default Configuration Which Leads to Denial of Service via Unbounded HTTP/3 Header Size

## Summary
Severity: High
Advisory: GHSA-c2rx-5r8w-8xr2
CVE: CVE-2026-44892
CWE: CWE-1188, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-c2rx-5r8w-8xr2
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http3` — affected >=4.2.0.Final <4.2.15.Final

## Details
### Summary
The default configuration of the `Http3ConnectionHandler` in the Netty HTTP/3 codec lacks an enforced maximum header size limit. When a peer does not explicitly specify `HTTP3_SETTINGS_MAX_FIELD_SECTION_SIZE`, the implementation defaults to an unbounded limit. This insecure default configuration allows a malicious client or server to send an enormous number of headers, leading to a memory exhaustion Denial of Service via an `OutOfMemoryError`.

### Details
Netty securely limits header sizes for older protocols. In HTTP/1.1, Netty strictly enforces an `8192`-byte limit out-of-the-box via `HttpObjectDecoder`. For HTTP/2, while RFC 9113 specifies that `SETTINGS_MAX_HEADER_LIST_SIZE` defaults to `unlimited`, Netty securely overrides this RFC default by enforcing an `8192`-byte limit (`Http2CodecUtil.DEFAULT_HEADER_LIST_SIZE`).

However, this secure-by-default configuration is missing in the HTTP/3 implementation. While Netty provides a mechanism to configure the maximum header field section size via `Http3Settings`, its out-of-the-box behaviour strictly follows RFC 9114's unlimited default.

Because many developers rely on the framework's default configurations and basic constructors, their applications are unknowingly left vulnerable. This nearly infinite default limit is passed into `Http3FrameCodec#newFactory` and stored as `maxHeaderListSize` inside `Http3FrameCodec`.

A bad actor can continuously send HTTP/3 headers within a connection, exploiting the insecure default configuration to consume server memory unconditionally until the application crashes with an `OutOfMemoryError`.

### Impact
Denial of Service via memory exhaustion. All applications using Netty's HTTP/3 codec with its default configuration are impacted.

## References
- https://github.com/netty/netty/security/advisories/GHSA-c2rx-5r8w-8xr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-44892
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
