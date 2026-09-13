# [H] RDMA/hfi1: Fix use-after-free bug for mm struct

## Summary
Severity: High
Advisory: CVE-2022-49076
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49076
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hfi1: Fix use-after-free bug for mm struct

Under certain conditions, such as MPI_Abort, the hfi1 cleanup code may
represent the last reference held on the task mm.
hfi1_mmu_rb_unregister() then drops the last reference and the mm is freed
before the final use in hfi1_release_user_pages().  A new task may
allocate the mm structure while it is still being used, resulting in
problems. One manifestation is corruption of the mmap_sem counter leading
to a hang in down_write().  Another is corruption of an mm struct that is
in use by another task.

## References
- https://git.kernel.org/stable/c/0b7186d657ee55e2cdefae498f07d5c1961e8023
- https://git.kernel.org/stable/c/2bbac98d0930e8161b1957dc0ec99de39ade1b3c
- https://git.kernel.org/stable/c/5a9a1b24ddb510715f8f621263938186579a965c
- https://git.kernel.org/stable/c/5f54364ff6cfcd14cddf5441c4a490bb28dd69f7
- https://git.kernel.org/stable/c/9ca11bd8222a612de0d2f54d050bfcf61ae2883f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49076.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
