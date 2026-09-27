# [M] CVE-2021-47296

## Summary
Severity: Medium
Advisory: CVE-2021-47296
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47296
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: PPC: Fix kvm_arch_vcpu_ioctl vcpu_load leak

vcpu_put is not called if the user copy fails. This can result in preempt
notifier corruption and crashes, among other issues.

## References
- https://git.kernel.org/stable/c/bc4188a2f56e821ea057aca6bf444e138d06c252
- https://git.kernel.org/stable/c/e14ef1095387f764d95614d3ec9e4d07c82a3533
- https://git.kernel.org/stable/c/f38527f1890543cdfca8dfd06f75f9887cce6151
- https://git.kernel.org/stable/c/9bafc34dc4ad0cef18727c557f21ed3c3304df50
- https://git.kernel.org/stable/c/a4a488915feaad38345cc01b80d52e8200ff5209
