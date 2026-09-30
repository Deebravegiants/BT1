# [H] CVE-2017-9751

## Summary
Severity: High
Advisory: CVE-2017-9751
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9751
Type: osv

## Details
opcodes/rl78-decode.opc in GNU Binutils 2.28 has an unbounded GETBYTE macro, which allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, as demonstrated by mishandling of this file during "objdump -D" execution.

## References
- http://www.securityfocus.com/bid/99111
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=21588
