# [M] CVE-2017-15306

## Summary
Severity: Medium
Advisory: CVE-2017-15306
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-06
Source: https://osv.dev/vulnerability/CVE-2017-15306
Type: osv

## Details
The kvm_vm_ioctl_check_extension function in arch/powerpc/kvm/powerpc.c in the Linux kernel before 4.13.11 allows local users to cause a denial of service (NULL pointer dereference and system crash) via a KVM_CHECK_EXTENSION KVM_CAP_PPC_HTM ioctl call to /dev/kvm.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.11
- http://www.securityfocus.com/bid/101693
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ac64115a66c18c01745bbd3c47a36b124e5fd8c0
- http://openwall.com/lists/oss-security/2017/11/06/6
- https://github.com/torvalds/linux/commit/ac64115a66c18c01745bbd3c47a36b124e5fd8c0
