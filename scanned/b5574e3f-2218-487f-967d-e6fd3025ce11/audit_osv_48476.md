# [H] CVE-2017-8061

## Summary
Severity: High
Advisory: CVE-2017-8061
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8061
Type: osv

## Details
drivers/media/usb/dvb-usb/dvb-usb-firmware.c in the Linux kernel 4.9.x and 4.10.x before 4.10.7 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.7
- http://www.securityfocus.com/bid/97972
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=67b0503db9c29b04eadfeede6bebbfe5ddad94ef
- https://github.com/torvalds/linux/commit/67b0503db9c29b04eadfeede6bebbfe5ddad94ef
- http://www.openwall.com/lists/oss-security/2017/04/16/4
