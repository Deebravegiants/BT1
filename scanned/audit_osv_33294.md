# [H] binder: fix double-free in dbitmap

## Summary
Severity: High
Advisory: CVE-2025-40028
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40028
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.52, >=6.13.0 <6.16.12, >=6.17.0 <6.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix double-free in dbitmap

A process might fail to allocate a new bitmap when trying to expand its
proc->dmap. In that case, dbitmap_grow() fails and frees the old bitmap
via dbitmap_free(). However, the driver calls dbitmap_free() again when
the same process terminates, leading to a double-free error:

  ==================================================================
  BUG: KASAN: double-free in binder_proc_dec_tmpref+0x2e0/0x55c
  Free of addr ffff00000b7c1420 by task kworker/9:1/209

  CPU: 9 UID: 0 PID: 209 Comm: kworker/9:1 Not tainted 6.17.0-rc6-dirty #5 PREEMPT
  Hardware name: linux,dummy-virt (DT)
  Workqueue: events binder_deferred_func
  Call trace:
   kfree+0x164/0x31c
   binder_proc_dec_tmpref+0x2e0/0x55c
   binder_deferred_func+0xc24/0x1120
   process_one_work+0x520/0xba4
  [...]

  Allocated by task 448:
   __kmalloc_noprof+0x178/0x3c0
   bitmap_zalloc+0x24/0x30
   binder_open+0x14c/0xc10
  [...]

  Freed by task 449:
   kfree+0x184/0x31c
   binder_inc_ref_for_node+0xb44/0xe44
   binder_transaction+0x29b4/0x7fbc
   binder_thread_write+0x1708/0x442c
   binder_ioctl+0x1b50/0x2900
  [...]
  ==================================================================

Fix this issue by marking proc->map NULL in dbitmap_free().

## References
- https://git.kernel.org/stable/c/0390633979969c54c0ce6a198d6f45cdbe2c84b1
- https://git.kernel.org/stable/c/3ebcd3460cad351f198c39c6edb4af519a0ed934
- https://git.kernel.org/stable/c/b781e5635a3398e2b64440371233c2c5102cd6cb
- https://git.kernel.org/stable/c/c301ec61ce6f16e21a36b99225ca8a20c1591e10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40028.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
