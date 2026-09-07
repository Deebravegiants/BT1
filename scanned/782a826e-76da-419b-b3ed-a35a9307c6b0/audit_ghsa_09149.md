# [M] netty-incubator-codec-ohttp's HPKEContext operations may produce empty byte[] on failures

## Summary
Severity: Medium
Advisory: GHSA-f659-372h-6x3x
CVE: CVE-2026-41207
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-f659-372h-6x3x
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp` — affected >=0 <0.0.21.Final

## Details
HKDF_expand: returns non-NULL on failure. The byte[] is filled with zeros and has no way to distinguish success from failure. Since this output is used as HKDF key material for the response AEAD, a  failure silently produces an all-zero key.

When EVP_HPKE_CTX_export fails it also returns an empty byte[] array filled with zeros. This byte[] feeds directly into OHttpCrypto.createResponseAEAD(...).  A silent all-zero export secret would produce a deterministic, attacker-predictable AEAD key.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-f659-372h-6x3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-41207
- https://github.com/netty/netty-incubator-codec-ohttp/commit/3d3b4e527fc82ad0fe3db1af951ffd0ec9a10680
- https://github.com/netty/netty-incubator-codec-ohttp
