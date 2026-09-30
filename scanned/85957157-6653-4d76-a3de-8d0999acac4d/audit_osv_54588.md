# [M] CVE-2024-1312

## Summary
Severity: Medium
Advisory: CVE-2024-1312
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-1312
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel's Memory Management subsystem when a user wins two races at the same time with a fail in the mas_prev_slot function. This issue could allow a local user to crash the system.

## References
- https://access.redhat.com/security/cve/CVE-2024-1312
- https://bugzilla.redhat.com/show_bug.cgi?id=2225569
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/mm/memory.c?h=v6.8-rc3&id=657b5146955eba331e01b9a6ae89ce2e716ba306
