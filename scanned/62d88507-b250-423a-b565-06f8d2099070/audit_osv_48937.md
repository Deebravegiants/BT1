# [H] CVE-2018-18445

## Summary
Severity: High
Advisory: CVE-2018-18445
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-18445
Type: osv

## Details
In the Linux kernel 4.14.x, 4.15.x, 4.16.x, 4.17.x, and 4.18.x before 4.18.13, faulty computation of numeric bounds in the BPF verifier permits out-of-bounds memory accesses because adjust_scalar_min_max_vals in kernel/bpf/verifier.c mishandles 32-bit right shifts.

## References
- https://usn.ubuntu.com/3835-1/
- https://usn.ubuntu.com/3847-1/
- https://usn.ubuntu.com/3847-3/
- https://support.f5.com/csp/article/K38456756
- https://usn.ubuntu.com/3832-1/
- https://usn.ubuntu.com/3847-2/
- https://access.redhat.com/errata/RHSA-2019:0512
- https://access.redhat.com/errata/RHSA-2019:0514
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b799207e1e1816b09e7a5920fbb2d5fcf6edd681
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1686
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.75
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.13
- https://github.com/torvalds/linux/commit/b799207e1e1816b09e7a5920fbb2d5fcf6edd681
