# [H] CVE-2023-46813

## Summary
Severity: High
Advisory: CVE-2023-46813
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-27
Source: https://osv.dev/vulnerability/CVE-2023-46813
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.5.9, exploitable by local users with userspace access to MMIO registers. Incorrect access checking in the #VC handler and instruction emulation of the SEV-ES emulation of MMIO accesses could lead to arbitrary write access to kernel memory (and thus privilege escalation). This depends on a race condition through which userspace can replace an instruction before the #VC handler reads it.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://bugzilla.suse.com/show_bug.cgi?id=1212649
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=63e44bc52047f182601e7817da969a105aa1f721
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a37cd2a59d0cb270b1bba568fd3a3b8668b9d3ba
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b9cb9c45583b911e0db71d09caa6b56469eb2bdf
