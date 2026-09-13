# [M] CVE-2023-3355

## Summary
Severity: Medium
Advisory: CVE-2023-3355
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-28
Source: https://osv.dev/vulnerability/CVE-2023-3355
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel's drivers/gpu/drm/msm/msm_gem_submit.c code in the submit_lookup_cmds function, which fails because it lacks a check of the return value of kmalloc(). This issue allows a local user to crash the system.

## References
- https://access.redhat.com/security/cve/CVE-2023-3355
- https://bugzilla.redhat.com/show_bug.cgi?id=2217820
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d839f0811a31322c087a859c2b181e2383daa7be
