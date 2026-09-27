# [M] CVE-2024-50382

## Summary
Severity: Medium
Advisory: CVE-2024-50382
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-23
Source: https://osv.dev/vulnerability/CVE-2024-50382
Type: osv

## Details
Botan before 3.6.0, when certain LLVM versions are used, has compiler-induced secret-dependent control flow in lib/utils/ghash/ghash.cpp in GHASH in AES-GCM. There is a branch instead of an XOR with carry. This was observed for Clang in LLVM 15 on RISC-V.

## References
- https://arxiv.org/pdf/2410.13489
- https://github.com/randombit/botan/compare/3.5.0...3.6.0
- https://news.ycombinator.com/item?id=41887153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50382.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50382
- https://github.com/randombit/botan/commit/53b0cfde580e86b03d0d27a488b6c134f662e957
