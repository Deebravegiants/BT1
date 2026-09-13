# [H] CVE-2017-9763

## Summary
Severity: High
Advisory: CVE-2017-9763
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-9763
Type: osv

## Details
The grub_ext2_read_block function in fs/ext2.c in GNU GRUB before 2013-11-12, as used in shlr/grub/fs/ext2.c in radare2 1.5.0, allows remote attackers to cause a denial of service (excessive stack use and application crash) via a crafted binary file, related to use of a variable-size stack array.

## References
- http://www.securityfocus.com/bid/99141
- http://git.savannah.gnu.org/cgit/grub.git/commit/grub-core/fs/ext2.c?id=ac8cac1dac50daaf1c390d701cca3b55e16ee768
- https://github.com/radare/radare2/commit/65000a7fd9eea62359e6d6714f17b94a99a82edd
- https://github.com/radare/radare2/issues/7723
