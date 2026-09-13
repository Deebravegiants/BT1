# [H] CVE-2016-9777

## Summary
Severity: High
Advisory: CVE-2016-9777
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9777
Type: osv

## Details
KVM in the Linux kernel before 4.8.12, when I/O APIC is enabled, does not properly restrict the VCPU index, which allows guest OS users to gain host OS privileges or cause a denial of service (out-of-bounds array access and host OS crash) via a crafted interrupt request, related to arch/x86/kvm/ioapic.c and arch/x86/kvm/ioapic.h.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.12
- http://www.securityfocus.com/bid/94640
- https://bugzilla.redhat.com/show_bug.cgi?id=1400804
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=81cdb259fb6d8c1c4ecfeea389ff5a73c07f5755
- http://www.openwall.com/lists/oss-security/2016/12/02/2
- https://github.com/torvalds/linux/commit/81cdb259fb6d8c1c4ecfeea389ff5a73c07f5755
