# [H] netty-incubator-codec-ohttp: [OHttpServerCodec] Native Direct-Memory Leak on AEAD Decryption Failure Leads to Gateway Denial of Service

## Summary
Severity: High
Advisory: GHSA-vmr9-j6wf-pmh2
CVE: CVE-2026-54251
CWE: CWE-664
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-vmr9-j6wf-pmh2
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp` — affected >=0 <0.0.23.Final

## Details
The **netty-incubator-codec-ohttp** library implements Oblivious HTTP (OHTTP) gateway and client functionality using Netty's `ByteBuf` memory management. When an OHTTP gateway processes encrypted client requests, it allocates a pooled direct (native off-heap) `ByteBuf` to hold the decrypted plaintext before the AEAD tag is verified. If the AEAD tag check fails — meaning the ciphertext is invalid — the decryption method throws a `CryptoException`, but the allocated buffer is never released because no `try/finally` block guards the allocation.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-vmr9-j6wf-pmh2
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/releases/tag/netty-incubator-codec-parent-ohttp-0.0.23.Final
