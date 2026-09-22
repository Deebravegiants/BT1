# [H] bpf, test_run: Fix alignment problem in bpf_prog_test_run_skb()

## Summary
Severity: High
Advisory: CVE-2022-49840
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49840
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.156, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, test_run: Fix alignment problem in bpf_prog_test_run_skb()

We got a syzkaller problem because of aarch64 alignment fault
if KFENCE enabled. When the size from user bpf program is an odd
number, like 399, 407, etc, it will cause the struct skb_shared_info's
unaligned access. As seen below:

  BUG: KFENCE: use-after-free read in __skb_clone+0x23c/0x2a0 net/core/skbuff.c:1032

  Use-after-free read at 0xffff6254fffac077 (in kfence-#213):
   __lse_atomic_add arch/arm64/include/asm/atomic_lse.h:26 [inline]
   arch_atomic_add arch/arm64/include/asm/atomic.h:28 [inline]
   arch_atomic_inc include/linux/atomic-arch-fallback.h:270 [inline]
   atomic_inc include/asm-generic/atomic-instrumented.h:241 [inline]
   __skb_clone+0x23c/0x2a0 net/core/skbuff.c:1032
   skb_clone+0xf4/0x214 net/core/skbuff.c:1481
   ____bpf_clone_redirect net/core/filter.c:2433 [inline]
   bpf_clone_redirect+0x78/0x1c0 net/core/filter.c:2420
   bpf_prog_d3839dd9068ceb51+0x80/0x330
   bpf_dispatcher_nop_func include/linux/bpf.h:728 [inline]
   bpf_test_run+0x3c0/0x6c0 net/bpf/test_run.c:53
   bpf_prog_test_run_skb+0x638/0xa7c net/bpf/test_run.c:594
   bpf_prog_test_run kernel/bpf/syscall.c:3148 [inline]
   __do_sys_bpf kernel/bpf/syscall.c:4441 [inline]
   __se_sys_bpf+0xad0/0x1634 kernel/bpf/syscall.c:4381

  kfence-#213: 0xffff6254fffac000-0xffff6254fffac196, size=407, cache=kmalloc-512

  allocated by task 15074 on cpu 0 at 1342.585390s:
   kmalloc include/linux/slab.h:568 [inline]
   kzalloc include/linux/slab.h:675 [inline]
   bpf_test_init.isra.0+0xac/0x290 net/bpf/test_run.c:191
   bpf_prog_test_run_skb+0x11c/0xa7c net/bpf/test_run.c:512
   bpf_prog_test_run kernel/bpf/syscall.c:3148 [inline]
   __do_sys_bpf kernel/bpf/syscall.c:4441 [inline]
   __se_sys_bpf+0xad0/0x1634 kernel/bpf/syscall.c:4381
   __arm64_sys_bpf+0x50/0x60 kernel/bpf/syscall.c:4381

To fix the problem, we adjust @size so that (@size + @hearoom) is a
multiple of SMP_CACHE_BYTES. So we make sure the struct skb_shared_info
is aligned to a cache line.

## References
- https://git.kernel.org/stable/c/047824a730699c6c66df43306b80f700c9dfc2fd
- https://git.kernel.org/stable/c/1b597f2d6a55e9f549989913860ad5170da04964
- https://git.kernel.org/stable/c/730fb1ef974a13915bc7651364d8b3318891cd70
- https://git.kernel.org/stable/c/7a704dbfd3735304e261f2787c52fbc7c3884736
- https://git.kernel.org/stable/c/d3fd203f36d46aa29600a72d57a1b61af80e4a25
- https://git.kernel.org/stable/c/e60f37a1d379c821c17b08f366412dce9ef3d99f
- https://git.kernel.org/stable/c/eaa8edd86514afac9deb9bf9a5053e74f37edf40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49840.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49840
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
