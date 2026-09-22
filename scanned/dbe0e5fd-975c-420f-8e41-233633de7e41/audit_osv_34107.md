# [H] Heap Buffer Overflow in NASA CryptoLib 1.4.0 `Crypto_TC_Check_IV_Setup`

## Summary
Severity: High
Advisory: CVE-2025-54878
Aliases: GHSA-9qph-pxfm-q9g4
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-54878
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. A heap buffer overflow vulnerability exists in NASA CryptoLib version 1.4.0 and prior in the IV setup logic for telecommand frames. The problem arises from missing bounds checks when copying the Initialization Vector (IV) into a freshly allocated buffer. An attacker can supply a crafted TC frame that causes the library to write one byte past the end of the heap buffer, leading to heap corruption and undefined behaviour. An attacker supplying a malformed telecommand frame can corrupt heap memory. This leads to undefined behaviour, which could manifest itself as a crash (denial of service) or more severe exploitation. This issue has been patched in version 1.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54878.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-9qph-pxfm-q9g4
- https://nvd.nist.gov/vuln/detail/CVE-2025-54878
- https://github.com/nasa/CryptoLib/commit/9b5b294ec09da450d2d4d05aea2db604ead48be1
