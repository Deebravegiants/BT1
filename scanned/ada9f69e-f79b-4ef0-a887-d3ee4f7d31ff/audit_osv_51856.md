# [H] CVE-2021-43057

## Summary
Severity: High
Advisory: CVE-2021-43057
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-28
Source: https://osv.dev/vulnerability/CVE-2021-43057
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.14.8. A use-after-free in selinux_ptrace_traceme (aka the SELinux handler for PTRACE_TRACEME) could be used by local attackers to cause memory corruption and escalate privileges, aka CID-a3727a8bac0a. This occurs because of an attempt to access the subjective credentials of another task.

## References
- https://security.netapp.com/advisory/ntap-20211125-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.8
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a3727a8bac0a9e77c70820655fd8715523ba3db7
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2229
