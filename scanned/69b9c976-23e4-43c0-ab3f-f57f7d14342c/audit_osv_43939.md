# [M] libcrux before 0.0.6 Cryptographic Implementation Bug Fixes

## Summary
Severity: Medium
Advisory: CVE-2026-76234
Aliases: GHSA-435g-fcv3-8j26, RUSTSEC-2026-0023, RUSTSEC-2026-0024, RUSTSEC-2026-0025, RUSTSEC-2026-0026
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76234
Type: osv

## Details
libcrux-ecdh and libcrux-ed25519 before 0.0.6, and libcrux-psq before 0.0.7, contain cryptographic implementation bugs. libcrux-ecdh did not properly check length and clamping during X25519 secret validation (and had a broken clamping check for imported X25519 secret keys); libcrux-ed25519 performed a duplicated clamping step during key generation; and libcrux-psq panicked instead of propagating an AEADError. These were fixed in the respective patched releases.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76234.json
- https://github.com/celabshq/libcrux/security/advisories/GHSA-435g-fcv3-8j26
- https://nvd.nist.gov/vuln/detail/CVE-2026-76234
- https://www.vulncheck.com/advisories/libcrux-before-cryptographic-implementation-bug-fixes
