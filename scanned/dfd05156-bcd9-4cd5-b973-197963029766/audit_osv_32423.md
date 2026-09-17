# [C] CryptoLib's Crypto_TC_Prep_AAD Has Buffer Overflow Due to Integer Underflow

## Summary
Severity: Critical
Advisory: CVE-2025-29913
Aliases: GHSA-q4v2-fvrv-qrf6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-17
Source: https://osv.dev/vulnerability/CVE-2025-29913
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. A critical heap buffer overflow vulnerability was identified in the `Crypto_TC_Prep_AAD` function of CryptoLib versions 1.3.3 and prior. This vulnerability allows an attacker to trigger a Denial of Service (DoS) or potentially execute arbitrary code (RCE) by providing a maliciously crafted telecommand (TC) frame that causes an unsigned integer underflow. The vulnerability lies in the function `Crypto_TC_Prep_AAD`, specifically during the computation of `tc_mac_start_index`. The affected code incorrectly calculates the MAC start index without ensuring it remains within the bounds of the `ingest` buffer. When `tc_mac_start_index` underflows due to an incorrect length calculation, the function attempts to access an out-of-bounds memory location, leading to a segmentation fault. The vulnerability is still present in the repository as of commit `d3cc420ace96d02a5b7e83d88cbd2e48010d5723`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29913.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-q4v2-fvrv-qrf6
- https://nvd.nist.gov/vuln/detail/CVE-2025-29913
