# [H] CVE-2016-9084

## Summary
Severity: High
Advisory: CVE-2016-9084
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-9084
Type: osv

## Details
drivers/vfio/pci/vfio_pci_intrs.c in the Linux kernel through 4.8.11 misuses the kzalloc function, which allows local users to cause a denial of service (integer overflow) or have unspecified other impact by leveraging access to a vfio PCI device file.

## References
- http://www.securityfocus.com/bid/93930
- http://rhn.redhat.com/errata/RHSA-2017-0386.html
- http://rhn.redhat.com/errata/RHSA-2017-0387.html
- http://www.openwall.com/lists/oss-security/2016/10/26/11
- https://bugzilla.redhat.com/show_bug.cgi?id=1389259
- https://github.com/torvalds/linux/commit/05692d7005a364add85c6e25a6c4447ce08f913a
- https://patchwork.kernel.org/patch/9373631/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=05692d7005a364add85c6e25a6c4447ce08f913a
