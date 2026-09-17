# [C] Out-of-bounds Read in AES-CFB-128 on X86-64 with AVX-512 Support

## Summary
Severity: Critical
Advisory: CVE-2026-28386
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-28386
Type: osv

## Details
Issue summary: Applications using AES-CFB128 encryption or decryption on
systems with AVX-512 and VAES support can trigger an out-of-bounds read
of up to 15 bytes when processing partial cipher blocks.

Impact summary: This out-of-bounds read may trigger a crash which leads to
Denial of Service for an application if the input buffer ends at a memory
page boundary and the following page is unmapped. There is no information
disclosure as the over-read bytes are not written to output.

The vulnerable code path is only reached when processing partial blocks
(when a previous call left an incomplete block and the current call provides
fewer bytes than needed to complete it). Additionally, the input buffer
must be positioned at a page boundary with the following page unmapped.
CFB mode is not used in TLS/DTLS protocols, which use CBC, GCM, CCM, or
ChaCha20-Poly1305 instead. For these reasons the issue was assessed as
Low severity according to our Security Policy.

Only x86-64 systems with AVX-512 and VAES instruction support are affected.
Other architectures and systems without VAES support use different code
paths that are not affected.

OpenSSL FIPS module in 3.6 version is affected by this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28386.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28386
- https://openssl-library.org/news/secadv/20260407.txt
- https://github.com/openssl/openssl/commit/61f428a2fc6671ede184a19f71e6e495f0689621
