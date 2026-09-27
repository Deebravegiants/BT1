# [H] iavf: fix out-of-bounds writes in iavf_get_ethtool_stats()

## Summary
Severity: High
Advisory: CVE-2026-31505
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31505
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iavf: fix out-of-bounds writes in iavf_get_ethtool_stats()

iavf incorrectly uses real_num_tx_queues for ETH_SS_STATS. Since the
value could change in runtime, we should use num_tx_queues instead.

Moreover iavf_get_ethtool_stats() uses num_active_queues while
iavf_get_sset_count() and iavf_get_stat_strings() use
real_num_tx_queues, which triggers out-of-bounds writes when we do
"ethtool -L" and "ethtool -S" simultaneously [1].

For example when we change channels from 1 to 8, Thread 3 could be
scheduled before Thread 2, and out-of-bounds writes could be triggered
in Thread 3:

Thread 1 (ethtool -L)       Thread 2 (work)        Thread 3 (ethtool -S)
iavf_set_channels()
...
iavf_alloc_queues()
-> num_active_queues = 8
iavf_schedule_finish_config()
                                                   iavf_get_sset_count()
                                                   real_num_tx_queues: 1
                                                   -> buffer for 1 queue
                                                   iavf_get_ethtool_stats()
                                                   num_active_queues: 8
                                                   -> out-of-bounds!
                            iavf_finish_config()
                            -> real_num_tx_queues = 8

Use immutable num_tx_queues in all related functions to avoid the issue.

[1]
 BUG: KASAN: vmalloc-out-of-bounds in iavf_add_one_ethtool_stat+0x200/0x270
 Write of size 8 at addr ffffc900031c9080 by task ethtool/5800

 CPU: 1 UID: 0 PID: 5800 Comm: ethtool Not tainted 6.19.0-enjuk-08403-g8137e3db7f1c #241 PREEMPT(full)
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
 Call Trace:
  <TASK>
  dump_stack_lvl+0x6f/0xb0
  print_report+0x170/0x4f3
  kasan_report+0xe1/0x180
  iavf_add_one_ethtool_stat+0x200/0x270
  iavf_get_ethtool_stats+0x14c/0x2e0
  __dev_ethtool+0x3d0c/0x5830
  dev_ethtool+0x12d/0x270
  dev_ioctl+0x53c/0xe30
  sock_do_ioctl+0x1a9/0x270
  sock_ioctl+0x3d4/0x5e0
  __x64_sys_ioctl+0x137/0x1c0
  do_syscall_64+0xf3/0x690
  entry_SYSCALL_64_after_hwframe+0x77/0x7f
 RIP: 0033:0x7f7da0e6e36d
 ...
  </TASK>

 The buggy address belongs to a 1-page vmalloc region starting at 0xffffc900031c9000 allocated at __dev_ethtool+0x3cc9/0x5830
 The buggy address belongs to the physical page: page: refcount:1 mapcount:0 mapping:0000000000000000
 index:0xffff88813a013de0 pfn:0x13a013
 flags: 0x200000000000000(node=0|zone=2)
 raw: 0200000000000000 0000000000000000 dead000000000122 0000000000000000
 raw: ffff88813a013de0 0000000000000000 00000001ffffffff 0000000000000000
 page dumped because: kasan: bad access detected

 Memory state around the buggy address:
  ffffc900031c8f80: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
  ffffc900031c9000: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 >ffffc900031c9080: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
                    ^
  ffffc900031c9100: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8
  ffffc900031c9180: f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8 f8

## References
- https://git.kernel.org/stable/c/1f931dee5b726df1940348ec31614d64bac03aa6
- https://git.kernel.org/stable/c/bb85741d2dc2be207353a412f51b83697fcbefcf
- https://git.kernel.org/stable/c/fdf902bf86a80bf15792a1d20a67a5302498d7f1
- https://git.kernel.org/stable/c/fecacfc95f195b99c71c579a472120d0b4ed65fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31505.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31505
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
