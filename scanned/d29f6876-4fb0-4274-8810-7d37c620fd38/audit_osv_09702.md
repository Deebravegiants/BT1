# [H] CVE-2017-10929

## Summary
Severity: High
Advisory: CVE-2017-10929
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/CVE-2017-10929
Type: osv

## Details
The grub_memmove function in shlr/grub/kern/misc.c in radare2 1.5.0 allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted binary file, possibly related to a read overflow in the grub_disk_read_small_real function in kern/disk.c in GNU GRUB 2.02.

## References
- http://www.securityfocus.com/bid/99608
- https://github.com/radare/radare2/issues/7855
- https://github.com/radare/radare2/commit/c57997e76ec70862174a1b3b3aeb62a6f8570e85
