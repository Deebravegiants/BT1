# [H] CryptoLib Has Out-of-bounds Read in Crypto_AOS_ProcessSecurity

## Summary
Severity: High
Advisory: CVE-2026-21898
Aliases: GHSA-7ch6-2pmg-m853
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-21898
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, the Crypto_AOS_ProcessSecurity function reads memory without valid bounds checking when parsing AOS frame hashes. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21898.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-7ch6-2pmg-m853
- https://nvd.nist.gov/vuln/detail/CVE-2026-21898
