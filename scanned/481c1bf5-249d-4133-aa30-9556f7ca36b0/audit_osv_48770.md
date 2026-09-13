# [M] CVE-2018-12904

## Summary
Severity: Medium
Advisory: CVE-2018-12904
CVSS: 4.9 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2018-06-27
Source: https://osv.dev/vulnerability/CVE-2018-12904
Type: osv

## Details
In arch/x86/kvm/vmx.c in the Linux kernel before 4.17.2, when nested virtualization is used, local attackers could cause L1 KVM guests to VMEXIT, potentially allowing privilege escalations and denial of service attacks due to lack of checking of CPL.

## References
- https://usn.ubuntu.com/3752-3/
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.2
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=727ba748e110b4de50d142edca9d6a9b7e6111d8
- https://github.com/torvalds/linux/commit/727ba748e110b4de50d142edca9d6a9b7e6111d8
- https://www.exploit-db.com/exploits/44944/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1589
