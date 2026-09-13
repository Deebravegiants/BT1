# [M] CVE-2023-30456

## Summary
Severity: Medium
Advisory: CVE-2023-30456
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-04-10
Source: https://osv.dev/vulnerability/CVE-2023-30456
Type: osv

## Details
An issue was discovered in arch/x86/kvm/vmx/nested.c in the Linux kernel before 6.2.8. nVMX on x86_64 lacks consistency checks for CR0 and CR4.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- http://packetstormsecurity.com/files/173757/Kernel-Live-Patch-Security-Notice-LSN-0096-1.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://security.netapp.com/advisory/ntap-20230511-0007/
- https://github.com/torvalds/linux/commit/112e66017bff7f2837030f34c2bc19501e9212d5
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.8
