# [H] CVE-2017-8066

## Summary
Severity: High
Advisory: CVE-2017-8066
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8066
Type: osv

## Details
drivers/net/can/usb/gs_usb.c in the Linux kernel 4.9.x and 4.10.x before 4.10.2 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.2
- http://www.securityfocus.com/bid/97992
- http://www.openwall.com/lists/oss-security/2017/04/16/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c919a3069c775c1c876bec55e00b2305d5125caa
- https://github.com/torvalds/linux/commit/c919a3069c775c1c876bec55e00b2305d5125caa
