# [M] CVE-2017-7224

## Summary
Severity: Medium
Advisory: CVE-2017-7224
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-22
Source: https://osv.dev/vulnerability/CVE-2017-7224
Type: osv

## Details
The find_nearest_line function in objdump in GNU Binutils 2.28 is vulnerable to an invalid write (of size 1) while disassembling a corrupt binary that contains an empty function name, leading to a program crash.

## References
- http://www.securityfocus.com/bid/97277
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=20892
