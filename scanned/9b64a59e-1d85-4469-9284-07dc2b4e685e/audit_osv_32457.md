# [C] Heap Buffer Overflow via Incomplete Length Check in `Crypto_TC_ApplySecurity`

## Summary
Severity: Critical
Advisory: CVE-2025-30356
Aliases: GHSA-6w2x-w7w3-85w2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-30356
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. In 1.3.3 and earlier, a heap buffer overflow vulnerability persists in the Crypto_TC_ApplySecurity function due to an incomplete validation check on the fl (frame length) field. Although CVE-2025-29912 addressed an underflow issue involving fl, the patch fails to fully prevent unsafe calculations. As a result, an attacker can still craft malicious frames that cause a negative tf_payload_len, which is then interpreted as a large unsigned value, leading to a heap buffer overflow in a memcpy call.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30356.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-6w2x-w7w3-85w2
- https://nvd.nist.gov/vuln/detail/CVE-2025-30356
- https://github.com/nasa/CryptoLib/commit/59d1bce7608c94c6131ef4877535075b0649799c
