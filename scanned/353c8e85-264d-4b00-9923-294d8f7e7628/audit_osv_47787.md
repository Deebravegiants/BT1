# [M] CVE-2017-12168

## Summary
Severity: Medium
Advisory: CVE-2017-12168
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-12168
Type: osv

## Details
The access_pmu_evcntr function in arch/arm64/kvm/sys_regs.c in the Linux kernel before 4.8.11 allows privileged KVM guest OS users to cause a denial of service (assertion failure and host OS crash) by accessing the Performance Monitors Cycle Count Register (PMCCNTR).

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.11
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9e3f7a29694049edd728e2400ab57ad7553e5aa9
- https://bugzilla.redhat.com/show_bug.cgi?id=1492984
- https://github.com/torvalds/linux/commit/9e3f7a29694049edd728e2400ab57ad7553e5aa9
