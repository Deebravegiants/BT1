# [M] CVE-2017-11731

## Summary
Severity: Medium
Advisory: CVE-2017-11731
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-29
Source: https://osv.dev/vulnerability/CVE-2017-11731
Type: osv

## Details
An invalid memory read vulnerability was found in the function OpCode (called from isLogicalOp and decompileIF) in util/decompile.c in Ming 0.4.8, which allows attackers to cause a denial of service via a crafted file.

## References
- http://somevulnsofadlab.blogspot.jp/2017/07/libminginvalid-memory-read-in-opcode.html
- https://github.com/libming/libming/issues/84
- https://security.gentoo.org/glsa/201904-24
