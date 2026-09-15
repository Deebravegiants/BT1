# [M] CVE-2025-46673

## Summary
Severity: Medium
Advisory: CVE-2025-46673
CVSS: 4.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-04-27
Source: https://osv.dev/vulnerability/CVE-2025-46673
Type: osv

## Details
NASA CryptoLib before 1.3.2 does not check whether the SA is in an operational state before use, possibly leading to a bypass of the Space Data Link Security protocol (SDLS).

## References
- https://github.com/nasa/CryptoLib/compare/v1.3.0...v1.3.1
- https://github.com/nasa/CryptoLib/compare/v1.3.1...v1.3.2
- https://securitybynature.fr/post/hacking-cryptolib/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46673.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46673
- https://github.com/nasa/CryptoLib/pull/286
- https://github.com/nasa/CryptoLib/pull/306
