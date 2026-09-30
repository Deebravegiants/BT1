# [H] CVE-2016-3713

## Summary
Severity: High
Advisory: CVE-2016-3713
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-3713
Type: osv

## Details
The msr_mtrr_valid function in arch/x86/kvm/mtrr.c in the Linux kernel before 4.6.1 supports MSR 0x2f8, which allows guest OS users to read or write to the kvm_arch_vcpu data structure, and consequently obtain sensitive information or cause a denial of service (system crash), via a crafted ioctl call.

## References
- http://www.openwall.com/lists/oss-security/2016/05/16/2
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.1
- https://github.com/torvalds/linux/commit/9842df62004f366b9fed2423e24df10542ee0dc5
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9842df62004f366b9fed2423e24df10542ee0dc5
- https://bugzilla.redhat.com/show_bug.cgi?id=1332139
