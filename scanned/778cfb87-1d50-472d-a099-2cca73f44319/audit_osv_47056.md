# [M] CVE-2015-8817

## Summary
Severity: Medium
Advisory: CVE-2015-8817
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8817
Type: osv

## Details
QEMU (aka Quick Emulator) built to use 'address_space_translate' to map an address to a MemoryRegionSection is vulnerable to an OOB r/w access issue. It could occur while doing pci_dma_read/write calls. Affects QEMU versions >= 1.6.0 and <= 2.3.1. A privileged user inside guest could use this flaw to crash the guest instance resulting in DoS.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2670.html
- http://rhn.redhat.com/errata/RHSA-2016-2671.html
- http://rhn.redhat.com/errata/RHSA-2016-2704.html
- http://rhn.redhat.com/errata/RHSA-2016-2705.html
- http://rhn.redhat.com/errata/RHSA-2016-2706.html
- http://www.openwall.com/lists/oss-security/2016/03/01/1
- http://www.openwall.com/lists/oss-security/2016/03/01/10
- https://lists.gnu.org/archive/html/qemu-stable/2016-01/msg00060.html
- http://www.openwall.com/lists/oss-security/2016/03/01/1
- http://www.openwall.com/lists/oss-security/2016/03/01/10
- https://bugzilla.redhat.com/show_bug.cgi?id=1300771
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=23820dbfc79d1c9dce090b4c555994f2bb6a69b3
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=c3c1bb99d1c11978d9ce94d1bdcf0705378c1459
