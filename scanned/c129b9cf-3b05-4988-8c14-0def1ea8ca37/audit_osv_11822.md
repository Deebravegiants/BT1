# [H] CVE-2017-9949

## Summary
Severity: High
Advisory: CVE-2017-9949
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9949
Type: osv

## Details
The grub_memmove function in shlr/grub/kern/misc.c in radare2 1.5.0 allows remote attackers to cause a denial of service (stack-based buffer underflow and application crash) or possibly have unspecified other impact via a crafted binary file, possibly related to a buffer underflow in fs/ext2.c in GNU GRUB 2.02.

## References
- http://www.securityfocus.com/bid/99305
- https://github.com/radare/radare2/commit/796dd28aaa6b9fa76d99c42c4d5ff8b257cc2191
- https://github.com/radare/radare2/issues/7683
