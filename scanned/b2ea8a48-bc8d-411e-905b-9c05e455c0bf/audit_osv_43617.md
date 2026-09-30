# [H] net: pktgen: fix proc entry use-after-free

## Summary
Severity: High
Advisory: CVE-2026-74479
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74479
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: pktgen: fix proc entry use-after-free

pktgen_change_name() replaces pkt_dev->entry while holding t->if_lock.
pktgen_remove_device() removes the same entry before
_rem_dev_from_if_list() takes that lock.

This allows the following interleaving:

  CPU 0 (NETDEV_CHANGENAME)       CPU 1 (kpktgend)
  if_lock(t)
  proc_remove(pkt_dev->entry)
                                  proc_remove(pkt_dev->entry)
  pkt_dev->entry = proc_create_data(...)
  if_unlock(t)

The kthread can pass the stale proc_dir_entry to proc_remove() after the
rename path has freed it. A reproducer with a widened race window reports:

  BUG: KASAN: slab-use-after-free in proc_remove+0x78/0x80
  Read of size 8 at addr ffff8881478fea70 by task kpktgend_0/67
  Call Trace:
   proc_remove+0x78/0x80
   pktgen_remove_device.isra.0+0x11c/0x4c0
   pktgen_thread_worker+0x1214/0x6bc0
   kthread+0x2c6/0x3b0
  Allocated by task 95:
   __proc_create+0x204/0x790
   proc_create_data+0x72/0xe0
   pktgen_thread_write+0xd61/0x1510
  Freed by task 28:
   kmem_cache_free+0xcb/0x3d0
   proc_free_inode+0x5b/0x80
   rcu_core+0x50a/0x1850
  The buggy address belongs to the object at ffff8881478fea00
   which belongs to the cache proc_dir_entry of size 192

Move proc_remove() into the if_lock-protected list removal helper. Keep it
before list_del_rcu() to preserve the ordering required by add_device().
The rename path must then finish replacing the entry before removal, or
it observes that the device is no longer on the list.

## References
- https://git.kernel.org/stable/c/4ef801b838d85c0ea5852c50667f7344ce3b6cd0
- https://git.kernel.org/stable/c/577443530cb592d5782a1f79847411a9363a65c8
- https://git.kernel.org/stable/c/7991c7cff8b8622cddb3d8dee07dbe74aa4cbec4
- https://git.kernel.org/stable/c/817ff6efdb7f484ea547218e11e17d8e43daa3b4
- https://git.kernel.org/stable/c/82ed3db9269cb61e3c15bad2f6e221efce90e1e0
- https://git.kernel.org/stable/c/b006a5404470bd3eb2aa0425fc447183032047ef
- https://git.kernel.org/stable/c/d1cc9797cf8f7aeb87e7ad01b748c6a960a819e4
- https://git.kernel.org/stable/c/f85a58340b91f225de3299dfa782c6414098077c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74479.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
