# [H] misc: fastrpc: take fl->lock when moving mmaps on interrupted invoke

## Summary
Severity: High
Advisory: CVE-2026-74646
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74646
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: take fl->lock when moving mmaps on interrupted invoke

When an invoke is interrupted by a signal,
wait_for_completion_interruptible() returns -ERESTARTSYS and
fastrpc_internal_invoke() moves every buffer from fl->mmaps onto
cctx->invoke_interrupted_mmaps. This list_del()/list_add_tail() walk
runs without holding fl->lock, the lock that serialises fl->mmaps in
fastrpc_req_mmap() and fastrpc_req_munmap() everywhere else.

Take fl->lock around the move, matching every other fl->mmaps accessor.

## References
- https://git.kernel.org/stable/c/3f265e405e5ef85030c3777262e18bb556bc8724
- https://git.kernel.org/stable/c/a902fe1f80f58a2335b6be1131866f827ec44d1a
- https://git.kernel.org/stable/c/af6345159abcbaa550518f31990d2a9558c2d369
- https://git.kernel.org/stable/c/b85a0e91d7d6cd06a53c881a46f749cfcef416a2
- https://git.kernel.org/stable/c/efd02f8d1a7449f15809bc18d3cd41aafea75d7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74646.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74646
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
