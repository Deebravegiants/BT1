# [H] CVE-2017-5547

## Summary
Severity: High
Advisory: CVE-2017-5547
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-5547
Type: osv

## Details
drivers/hid/hid-corsair.c in the Linux kernel 4.9.x before 4.9.6 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6
- http://www.securityfocus.com/bid/95709
- http://www.openwall.com/lists/oss-security/2017/01/21/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1416096
- https://github.com/torvalds/linux/commit/6d104af38b570d37aa32a5803b04c354f8ed513d
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6d104af38b570d37aa32a5803b04c354f8ed513d
