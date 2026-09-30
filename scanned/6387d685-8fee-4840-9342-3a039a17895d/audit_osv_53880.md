# [M] CVE-2023-29935

## Summary
Severity: Medium
Advisory: CVE-2023-29935
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-05
Source: https://osv.dev/vulnerability/CVE-2023-29935
Type: osv

## Details
llvm-project commit a0138390 was discovered to contain an assertion failure at !replacements.count(op) && "operation was already replaced.

## References
- https://github.com/llvm/llvm-project/issues/59182
