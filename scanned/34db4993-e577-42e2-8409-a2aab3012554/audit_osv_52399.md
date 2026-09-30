# [M] CVE-2021-47407

## Summary
Severity: Medium
Advisory: CVE-2021-47407
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47407
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Handle SRCU initialization failure during page track init

Check the return of init_srcu_struct(), which can fail due to OOM, when
initializing the page track mechanism.  Lack of checking leads to a NULL
pointer deref found by a modified syzkaller.

[Move the call towards the beginning of kvm_arch_init_vm. - Paolo]

## References
- https://git.kernel.org/stable/c/4664318f73e496cd22c71b10888e75434a123e23
- https://git.kernel.org/stable/c/deb2949417677649e2413266d7ce8c2ff73952b4
- https://git.kernel.org/stable/c/eb7511bf9182292ef1df1082d23039e856d1ddfb
