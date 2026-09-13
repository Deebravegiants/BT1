# [H] CVE-2024-37880

## Summary
Severity: High
Advisory: CVE-2024-37880
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-10
Source: https://osv.dev/vulnerability/CVE-2024-37880
Type: osv

## Details
The Kyber reference implementation before 9b8d306, when compiled by LLVM Clang through 18.x with some common optimization options, has a timing side channel that allows attackers to recover an ML-KEM 512 secret key in minutes. This occurs because poly_frommsg in poly.c does not prevent Clang from emitting a vulnerable secret-dependent branch.

## References
- https://news.ycombinator.com/item?id=40577486
- https://pqshield.com/pqshield-plugs-timing-leaks-in-kyber-ml-kem-to-improve-pqc-implementation-maturity/
- https://twitter.com/purnaltoon/status/1797644696568959476
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37880
- https://github.com/pq-crystals/kyber/commit/9b8d30698a3e7449aeb34e62339d4176f11e3c6c
- https://github.com/antoonpurnal/clangover
