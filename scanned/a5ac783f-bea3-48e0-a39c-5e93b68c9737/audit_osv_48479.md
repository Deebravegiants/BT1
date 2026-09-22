# [H] CVE-2017-8064

## Summary
Severity: High
Advisory: CVE-2017-8064
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8064
Type: osv

## Details
drivers/media/usb/dvb-usb-v2/dvb_usb_core.c in the Linux kernel 4.9.x and 4.10.x before 4.10.12 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=005145378c9ad7575a01b6ce1ba118fb427f583a
- https://github.com/torvalds/linux/commit/005145378c9ad7575a01b6ce1ba118fb427f583a
- http://www.debian.org/security/2017/dsa-3886
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.12
- http://www.securityfocus.com/bid/97975
- http://www.openwall.com/lists/oss-security/2017/04/16/4
