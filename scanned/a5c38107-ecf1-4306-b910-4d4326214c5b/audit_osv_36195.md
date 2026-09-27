# [M] CryptoLib Has Out-of-Bounds Read in KMC Encrypt Metadata Parsing via Flawed strtok Pattern

## Summary
Severity: Medium
Advisory: CVE-2026-21900
Aliases: GHSA-4g6v-36fv-qcvw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-21900
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, an out-of-bounds heap read vulnerability in cryptography_encrypt() occurs when parsing JSON metadata from KMC server responses. The flawed strtok iteration pattern uses ptr + strlen(ptr) + 1 which reads one byte past allocated buffer boundaries when processing short or malformed metadata strings. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21900.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-4g6v-36fv-qcvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-21900
- https://github.com/nasa/CryptoLib/commit/2372efd3da1ccb226b4297222e25f41ecc84821d
