# [C] CVE-2024-48949

## Summary
Severity: Critical
Advisory: CVE-2024-48949
Aliases: GHSA-434g-2637-qmqr
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-10
Source: https://osv.dev/vulnerability/CVE-2024-48949
Type: osv

## Details
The verify function in lib/elliptic/eddsa/index.js in the Elliptic package before 6.5.6 for Node.js omits "sig.S().gte(sig.eddsa.curve.n) || sig.S().isNeg()" validation.

## References
- https://github.com/indutny/elliptic/compare/v6.5.5...v6.5.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48949.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48949
- https://security.netapp.com/advisory/ntap-20241227-0003/
- https://github.com/indutny/elliptic/commit/7ac5360118f74eb02da73bdf9f24fd0c72ff5281
- https://blog.trailofbits.com/2025/11/18/we-found-cryptography-bugs-in-the-elliptic-library-using-wycheproof/
