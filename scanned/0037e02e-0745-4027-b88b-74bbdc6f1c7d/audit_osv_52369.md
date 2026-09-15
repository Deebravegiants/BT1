# [M] CVE-2021-47376

## Summary
Severity: Medium
Advisory: CVE-2021-47376
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47376
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Add oversize check before call kvcalloc()

Commit 7661809d493b ("mm: don't allow oversized kvmalloc() calls") add the
oversize check. When the allocation is larger than what kmalloc() supports,
the following warning triggered:

WARNING: CPU: 0 PID: 8408 at mm/util.c:597 kvmalloc_node+0x108/0x110 mm/util.c:597
Modules linked in:
CPU: 0 PID: 8408 Comm: syz-executor221 Not tainted 5.14.0-syzkaller #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/01/2011
RIP: 0010:kvmalloc_node+0x108/0x110 mm/util.c:597
Call Trace:
 kvmalloc include/linux/mm.h:806 [inline]
 kvmalloc_array include/linux/mm.h:824 [inline]
 kvcalloc include/linux/mm.h:829 [inline]
 check_btf_line kernel/bpf/verifier.c:9925 [inline]
 check_btf_info kernel/bpf/verifier.c:10049 [inline]
 bpf_check+0xd634/0x150d0 kernel/bpf/verifier.c:13759
 bpf_prog_load kernel/bpf/syscall.c:2301 [inline]
 __sys_bpf+0x11181/0x126e0 kernel/bpf/syscall.c:4587
 __do_sys_bpf kernel/bpf/syscall.c:4691 [inline]
 __se_sys_bpf kernel/bpf/syscall.c:4689 [inline]
 __x64_sys_bpf+0x78/0x90 kernel/bpf/syscall.c:4689
 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
 do_syscall_64+0x3d/0xb0 arch/x86/entry/common.c:80
 entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/0e6491b559704da720f6da09dd0a52c4df44c514
- https://git.kernel.org/stable/c/6345a0bee80139ea00a341c4202ebfd1534b5eb0
- https://git.kernel.org/stable/c/93937596e0652d50973f9dc944fea1694ac8cdfd
- https://git.kernel.org/stable/c/b5fe7cdfee5901ce5513c30e554d51536e003bde
