# [M] CVE-2024-50383

## Summary
Severity: Medium
Advisory: CVE-2024-50383
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-23
Source: https://osv.dev/vulnerability/CVE-2024-50383
Type: osv

## Details
Botan before 3.6.0, when certain GCC versions are used, has a compiler-induced secret-dependent operation in lib/utils/donna128.h in donna128 (used in Chacha-Poly1305 and x25519). An addition can be skipped if a carry is not set. This was observed for GCC 11.3.0 with -O2 on MIPS, and GCC on x86-i386. (Only 32-bit processors can be affected.)

## References
- https://arxiv.org/pdf/2410.13489
- https://github.com/randombit/botan/compare/3.5.0...3.6.0
- https://news.ycombinator.com/item?id=41887153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50383.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50383
- https://github.com/randombit/botan/commit/53b0cfde580e86b03d0d27a488b6c134f662e957
