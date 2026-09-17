# [C] CryptoLib Has Heap Buffer Overflow Due to Unsigned Integer Underflow in Crypto_TC_ProcessSecurity

## Summary
Severity: Critical
Advisory: CVE-2025-29912
Aliases: GHSA-3f5x-r59x-p8cf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-17
Source: https://osv.dev/vulnerability/CVE-2025-29912
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. In versions 1.3.3 and prior, an unsigned integer underflow in the `Crypto_TC_ProcessSecurity` function of CryptoLib leads to a heap buffer overflow. The vulnerability is triggered when the `fl` (frame length) field in a Telecommand (TC) packet is set to 0. This underflow causes the frame length to be interpreted as 65535, resulting in out-of-bounds memory access. This critical vulnerability can be exploited to cause a denial of service (DoS) or potentially achieve remote code execution. Users of CryptoLib are advised to apply the recommended patch or avoid processing untrusted TC packets until a fix is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29912.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-3f5x-r59x-p8cf
- https://nvd.nist.gov/vuln/detail/CVE-2025-29912
- https://github.com/nasa/CryptoLib/commit/ca39cb96f21e76102aefb956d2c8c0ba0bd143ca
