# [M] netty-incubator-codec-ohttp's Incorrect Native Pointer Derivation in Pooled Direct ByteBuf Fallback Leads to Out-of-Bounds Native Memory Access

## Summary
Severity: Medium
Advisory: GHSA-32hf-8jw3-v4qq
CVE: CVE-2026-48040
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-32hf-8jw3-v4qq
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp-hpke-native-boringssl` — affected >=0 <0.0.22.Final

## Details
The netty-incubator-codec-ohttp library implements Oblivious HTTP (RFC 9458) using BoringSSL's HPKE C library via JNI. When deriving native memory addresses for cryptographic operations, provides a fallback path for direct ByteBufs that do not expose their memory address through `hasMemoryAddress()`. This fallback occurs when `sun.misc.Unsafe` is unavailable to Netty — for example, when the JVM is started with `-Dio.netty.noUnsafe=true`, when a SecurityManager restricts Unsafe access, or when running on non-HotSpot JVMs. In these configurations, Netty's default `PooledByteBufAllocator` returns `PooledDirectByteBuf` instances for which `hasMemoryAddress()` returns false.

**Why this matters:** Under the enabling JVM configuration, an unauthenticated network attacker can cause the OHTTP gateway to corrupt memory belonging to other concurrent connections and disclose the contents of adjacent pooled direct buffers by triggering cryptographic operations with crafted OHTTP requests. The corruption occurs regardless of whether the AEAD tag verification succeeds, as BoringSSL zeroizes the output buffer on failure. The information disclosure path provides the attacker with the encryption key needed to extract the leaked data. This violates the confidentiality and integrity of all connections sharing the same Netty buffer arena.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-32hf-8jw3-v4qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48040
- https://github.com/netty/netty-incubator-codec-ohttp/commit/7ad38d5cc2827af7e067e5c1e1ac37cd4566dad9
- https://github.com/netty/netty-incubator-codec-ohttp
