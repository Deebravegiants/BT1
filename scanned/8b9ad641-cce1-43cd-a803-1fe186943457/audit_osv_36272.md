# [H] CryptoLib Has Heap Buffer Overflow Vulnerability in KMC Base64 Decode Handling (KMC JSON base64ciphertext/base64cleartext)

## Summary
Severity: High
Advisory: CVE-2026-22697
Aliases: GHSA-qjx3-83jh-2jc4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22697
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, CryptoLib’s KMC crypto service integration is vulnerable to a heap buffer overflow when decoding Base64-encoded ciphertext/cleartext fields returned by the KMC service. The decode destination buffer is sized using an expected output length (len_data_out), but the Base64 decoder writes output based on the actual Base64 input length and does not enforce any destination size limit. An oversized Base64 string in the KMC JSON response can cause out-of-bounds writes on the heap, resulting in process crash and potentially code execution under certain conditions. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22697.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-qjx3-83jh-2jc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22697
