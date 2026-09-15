# [H] CVE-2017-8063

## Summary
Severity: High
Advisory: CVE-2017-8063
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8063
Type: osv

## Details
drivers/media/usb/dvb-usb/cxusb.c in the Linux kernel 4.9.x and 4.10.x before 4.10.12 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.12
- http://www.securityfocus.com/bid/97974
- http://www.openwall.com/lists/oss-security/2017/04/16/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3f190e3aec212fc8c61e202c51400afa7384d4bc
- https://github.com/torvalds/linux/commit/3f190e3aec212fc8c61e202c51400afa7384d4bc
