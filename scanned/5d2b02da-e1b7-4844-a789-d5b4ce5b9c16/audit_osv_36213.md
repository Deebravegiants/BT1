# [M] CryptoLib Unbounded Memory Allocation in KMC HTTP Response Handler Allows Resource Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-22026
Aliases: GHSA-w9cm-q69w-34x7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22026
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, the libcurl write_callback function in the KMC crypto service client allows unbounded memory growth by reallocating response buffers without any size limit or overflow check. A malicious KMC server can return arbitrarily large HTTP responses, forcing the client to allocate excessive memory until the process is terminated by the OS. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22026.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-w9cm-q69w-34x7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22026
- https://github.com/nasa/CryptoLib/commit/2372efd3da1ccb226b4297222e25f41ecc84821d
