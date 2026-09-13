# [H] CVE-2019-16718

## Summary
Severity: High
Advisory: CVE-2019-16718
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-23
Source: https://osv.dev/vulnerability/CVE-2019-16718
Type: osv

## Details
In radare2 before 3.9.0, a command injection vulnerability exists in bin_symbols() in libr/core/cbin.c. By using a crafted executable file, it's possible to execute arbitrary shell commands with the permissions of the victim. This vulnerability is due to an insufficient fix for CVE-2019-14745 and improper handling of symbol names embedded in executables.

## References
- https://github.com/radareorg/radare2/commit/dd739f5a45b3af3d1f65f00fe19af1dbfec7aea7
- https://github.com/radareorg/radare2/commit/5411543a310a470b1257fb93273cdd6e8dfcb3af
- https://github.com/radareorg/radare2/compare/3.8.0...3.9.0
