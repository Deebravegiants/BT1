# [M] CVE-2023-26924

## Summary
Severity: Medium
Advisory: CVE-2023-26924
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-26924
Type: osv

## Details
LLVM a0dab4950 has a segmentation fault in mlir::outlineSingleBlockRegion. NOTE: third parties dispute this because the LLVM security policy excludes "Language front-ends ... for which a malicious input file can cause undesirable behavior."

## References
- https://llvm.org/docs/Security.html#what-is-considered-a-security-issue
- https://gist.github.com/Colloportus0/fc16d10d74aedf89d5d1d020ebb89c0c
- https://github.com/llvm/llvm-project/issues/60216
