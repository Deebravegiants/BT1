# [H] CVE-2017-8069

## Summary
Severity: High
Advisory: CVE-2017-8069
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8069
Type: osv

## Details
drivers/net/usb/rtl8150.c in the Linux kernel 4.9.x before 4.9.11 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.11
- http://www.openwall.com/lists/oss-security/2017/04/16/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=7926aff5c57b577ab0f43364ff0c59d968f6a414
- https://github.com/torvalds/linux/commit/7926aff5c57b577ab0f43364ff0c59d968f6a414
