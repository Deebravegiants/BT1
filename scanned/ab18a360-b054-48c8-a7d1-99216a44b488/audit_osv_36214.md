# [H] CryptoLib Vulnerable to Heap Buffer Overflow in MariaDB SA Hexstring Conversion

## Summary
Severity: High
Advisory: CVE-2026-22027
Aliases: GHSA-3m35-m689-h29x
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22027
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, the convert_hexstring_to_byte_array() function in the MariaDB SA interface writes decoded bytes into a caller-provided buffer without any capacity check. When importing SA fields from the database (e.g., IV, ARSN, ABM), a malformed or oversized hex string in the database can overflow the destination buffer, corrupting adjacent heap memory. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22027.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-3m35-m689-h29x
- https://nvd.nist.gov/vuln/detail/CVE-2026-22027
- https://github.com/nasa/CryptoLib/commit/2372efd3da1ccb226b4297222e25f41ecc84821d
