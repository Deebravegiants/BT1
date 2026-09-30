# [H] CVE-2022-39189

## Summary
Severity: High
Advisory: CVE-2022-39189
Aliases: A-245869446, ASB-A-245869446
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-02
Source: https://osv.dev/vulnerability/CVE-2022-39189
Type: osv

## Details
An issue was discovered the x86 KVM subsystem in the Linux kernel before 5.18.17. Unprivileged guest users can compromise the guest kernel because TLB flush operations are mishandled in certain KVM_VCPU_PREEMPTED situations.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://www.debian.org/security/2023/dsa-5480
- https://security.netapp.com/advisory/ntap-20230214-0007/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2309
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.17
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6cd88243c7e03845a450795e134b488fc2afb736
- https://github.com/torvalds/linux/commit/6cd88243c7e03845a450795e134b488fc2afb736
