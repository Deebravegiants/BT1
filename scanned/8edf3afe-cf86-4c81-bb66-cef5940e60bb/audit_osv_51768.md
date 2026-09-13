# [M] CVE-2021-4001

## Summary
Severity: Medium
Advisory: CVE-2021-4001
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2021-4001
Type: osv

## Details
A race condition was found in the Linux kernel's ebpf verifier between bpf_map_update_elem and bpf_map_freeze due to a missing lock in kernel/bpf/syscall.c. In this flaw, a local user with a special privilege (cap_sys_admin or cap_bpf) can modify the frozen mapped address space. This flaw affects kernel versions prior to 5.16 rc2.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2025645
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf.git/commit/?id=353050be4c19e102178ccc05988101887c25ae53
