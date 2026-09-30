# [M] CVE-2019-19528

## Summary
Severity: Medium
Advisory: CVE-2019-19528
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19528
Type: osv

## Details
In the Linux kernel before 5.3.7, there is a use-after-free bug that can be caused by a malicious USB device in the drivers/usb/misc/iowarrior.c driver, aka CID-edc4746f253d.

## References
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.7
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c468a8aa790e0dfe0a7f8a39db282d39c2c00b46
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=edc4746f253d907d048de680a621e121517f484b
