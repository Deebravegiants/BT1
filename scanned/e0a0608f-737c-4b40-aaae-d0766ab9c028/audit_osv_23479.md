# [H] RDMA/cma: Do not change route.addr.src_addr outside state checks

## Summary
Severity: High
Advisory: CVE-2022-48925
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48925
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.103, >=5.11.0 <5.15.26, >=5.16.0 <5.16.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/cma: Do not change route.addr.src_addr outside state checks

If the state is not idle then resolve_prepare_src() should immediately
fail and no change to global state should happen. However, it
unconditionally overwrites the src_addr trying to build a temporary any
address.

For instance if the state is already RDMA_CM_LISTEN then this will corrupt
the src_addr and would cause the test in cma_cancel_operation():

           if (cma_any_addr(cma_src_addr(id_priv)) && !id_priv->cma_dev)

Which would manifest as this trace from syzkaller:

  BUG: KASAN: use-after-free in __list_add_valid+0x93/0xa0 lib/list_debug.c:26
  Read of size 8 at addr ffff8881546491e0 by task syz-executor.1/32204

  CPU: 1 PID: 32204 Comm: syz-executor.1 Not tainted 5.12.0-rc8-syzkaller #0
  Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/01/2011
  Call Trace:
   __dump_stack lib/dump_stack.c:79 [inline]
   dump_stack+0x141/0x1d7 lib/dump_stack.c:120
   print_address_description.constprop.0.cold+0x5b/0x2f8 mm/kasan/report.c:232
   __kasan_report mm/kasan/report.c:399 [inline]
   kasan_report.cold+0x7c/0xd8 mm/kasan/report.c:416
   __list_add_valid+0x93/0xa0 lib/list_debug.c:26
   __list_add include/linux/list.h:67 [inline]
   list_add_tail include/linux/list.h:100 [inline]
   cma_listen_on_all drivers/infiniband/core/cma.c:2557 [inline]
   rdma_listen+0x787/0xe00 drivers/infiniband/core/cma.c:3751
   ucma_listen+0x16a/0x210 drivers/infiniband/core/ucma.c:1102
   ucma_write+0x259/0x350 drivers/infiniband/core/ucma.c:1732
   vfs_write+0x28e/0xa30 fs/read_write.c:603
   ksys_write+0x1ee/0x250 fs/read_write.c:658
   do_syscall_64+0x2d/0x70 arch/x86/entry/common.c:46
   entry_SYSCALL_64_after_hwframe+0x44/0xae

This is indicating that an rdma_id_private was destroyed without doing
cma_cancel_listens().

Instead of trying to re-use the src_addr memory to indirectly create an
any address derived from the dst build one explicitly on the stack and
bind to that as any other normal flow would do. rdma_bind_addr() will copy
it over the src_addr once it knows the state is valid.

This is similar to commit bc0bdc5afaa7 ("RDMA/cma: Do not change
route.addr.src_addr.ss_family")

## References
- https://git.kernel.org/stable/c/00265efbd3e5705038c9492a434fda8cf960c8a2
- https://git.kernel.org/stable/c/22e9f71072fa605cbf033158db58e0790101928d
- https://git.kernel.org/stable/c/5b1cef5798b4fd6e4fd5522e7b8a26248beeacaa
- https://git.kernel.org/stable/c/d350724795c7a48b05bf921d94699fbfecf7da0b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48925.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
