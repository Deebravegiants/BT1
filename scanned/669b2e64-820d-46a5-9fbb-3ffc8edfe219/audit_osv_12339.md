# [M] CVE-2018-11384

## Summary
Severity: Medium
Advisory: CVE-2018-11384
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11384
Type: osv

## Details
The sh_op() function in radare2 2.5.0 allows remote attackers to cause a denial of service (heap-based out-of-bounds read and application crash) via a crafted ELF file.

## References
- https://github.com/radare/radare2/issues/9903
- https://github.com/radare/radare2/commit/77c47cf873dd55b396da60baa2ca83bbd39e4add
