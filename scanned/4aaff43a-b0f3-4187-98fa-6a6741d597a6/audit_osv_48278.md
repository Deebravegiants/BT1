# [H] CVE-2017-5548

## Summary
Severity: High
Advisory: CVE-2017-5548
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5548
Type: osv

## Details
drivers/net/ieee802154/atusb.c in the Linux kernel 4.9.x before 4.9.6 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6
- http://www.securityfocus.com/bid/95710
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=05a974efa4bdf6e2a150e3f27dc6fcf0a9ad5655
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416110
- https://github.com/torvalds/linux/commit/05a974efa4bdf6e2a150e3f27dc6fcf0a9ad5655
