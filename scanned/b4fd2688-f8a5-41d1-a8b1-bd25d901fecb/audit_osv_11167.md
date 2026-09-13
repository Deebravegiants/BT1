# [H] CVE-2017-6448

## Summary
Severity: High
Advisory: CVE-2017-6448
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2017-6448
Type: osv

## Details
The dalvik_disassemble function in libr/asm/p/asm_dalvik.c in radare2 1.2.1 allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted DEX file.

## References
- http://www.securityfocus.com/bid/97313
- https://github.com/radare/radare2/commit/f41e941341e44aa86edd4483c4487ec09a074257
- https://github.com/radare/radare2/issues/6885
