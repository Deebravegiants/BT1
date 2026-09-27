# [M] CVE-2017-1000252

## Summary
Severity: Medium
Advisory: CVE-2017-1000252
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-26
Source: https://osv.dev/vulnerability/CVE-2017-1000252
Type: osv

## Details
The KVM subsystem in the Linux kernel through 4.13.3 allows guest OS users to cause a denial of service (assertion failure, and hypervisor hang or crash) via an out-of bounds guest_irq value, related to arch/x86/kvm/vmx.c and virt/kvm/eventfd.c.

## References
- http://www.securityfocus.com/bid/101022
- http://www.debian.org/security/2017/dsa-3981
- https://access.redhat.com/errata/RHSA-2018:1130
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://bugzilla.redhat.com/show_bug.cgi?id=1490781
- https://github.com/torvalds/linux/commit/36ae3c0a36b7456432fedce38ae2f7bd3e01a563
- https://marc.info/?l=kvm&m=150549145711115&w=2
- https://github.com/torvalds/linux/commit/3a8b0677fc6180a467e26cc32ce6b0c09a32f9bb
- https://marc.info/?l=kvm&m=150549146311117&w=2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=36ae3c0a36b7456432fedce38ae2f7bd3e01a563
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3a8b0677fc6180a467e26cc32ce6b0c09a32f9bb
- http://www.openwall.com/lists/oss-security/2017/09/15/4
