# [C] CryptoLib Has Heap Buffer Overflow in Crypto_AOS_ProcessSecurity Function

## Summary
Severity: Critical
Advisory: CVE-2025-29911
Aliases: GHSA-7g6g-9gj4-8c68
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-17
Source: https://osv.dev/vulnerability/CVE-2025-29911
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. A critical heap buffer overflow vulnerability was identified in the `Crypto_AOS_ProcessSecurity` function of CryptoLib versions 1.3.3 and prior. This vulnerability allows an attacker to trigger a Denial of Service (DoS) or potentially execute arbitrary code (RCE) by providing a maliciously crafted AOS frame with an insufficient length. The vulnerability lies in the function `Crypto_AOS_ProcessSecurity`, specifically during the processing of the Frame Error Control Field (FECF). The affected code attempts to read from the `p_ingest` buffer at indices `current_managed_parameters_struct.max_frame_size - 2` and `current_managed_parameters_struct.max_frame_size - 1` without verifying if `len_ingest` is sufficiently large. This leads to a heap buffer overflow when `len_ingest` is smaller than `max_frame_size`. As of time of publication, no known patched versions exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29911.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-7g6g-9gj4-8c68
- https://nvd.nist.gov/vuln/detail/CVE-2025-29911
