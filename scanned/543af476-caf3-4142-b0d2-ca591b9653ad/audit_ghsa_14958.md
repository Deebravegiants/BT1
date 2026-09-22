# [M] BoringSSLAEADContext in Netty Repeats Nonces

## Summary
Severity: Medium
Advisory: GHSA-g762-h86w-8749
CVE: CVE-2024-36121
CWE: CWE-190, CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-g762-h86w-8749
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-ohttp` — affected >=0.0.3.Final <0.0.11.Final

## Details
### Summary
BoringSSLAEADContext keeps track of how many OHTTP responses have been sent and uses this sequence number to calculate the appropriate nonce to use with the encryption algorithm. 
Unfortunately, two separate errors combine which would allow an attacker to cause the sequence number to overflow and thus the nonce to repeat.

### Details
1. There is no overflow detection or enforcement of the maximum sequence value. (This is a missed requirement from the draft Chunked Oblivious OHTTP RFC and so should be inherited from the HPKE RFC 9180, Section 5.2).
2. The sequence number (seq) is stored as 32-bit int which is relatively easy to overflow.

https://github.com/netty/netty-incubator-codec-ohttp/blob/1ddadb6473cd3be5491d114431ed4c1a9f316001/codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAEADContext.java#L112-L114

### Impact
If the BoringSSLAEADContext is used to encrypt more than 2^32 messages then the AES-GCM nonce will repeat.
Repeating a nonce with AES-GCM results in both confidentiality and integrity compromise of data encrypted with the associated key.

## References
- https://github.com/netty/netty-incubator-codec-ohttp/security/advisories/GHSA-g762-h86w-8749
- https://nvd.nist.gov/vuln/detail/CVE-2024-36121
- https://github.com/netty/netty-incubator-codec-ohttp
- https://github.com/netty/netty-incubator-codec-ohttp/blob/1ddadb6473cd3be5491d114431ed4c1a9f316001/codec-ohttp-hpke-classes-boringssl/src/main/java/io/netty/incubator/codec/hpke/boringssl/BoringSSLAEADContext.java#L112-L114
