# [H] Bluetooth: Fix use-after-free bugs caused by sco_sock_timeout

## Summary
Severity: High
Advisory: CVE-2024-27398
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-27398
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.15.0 <6.1.91, >=5.16.0 <6.6.31, >=6.2.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Fix use-after-free bugs caused by sco_sock_timeout

When the sco connection is established and then, the sco socket
is releasing, timeout_work will be scheduled to judge whether
the sco disconnection is timeout. The sock will be deallocated
later, but it is dereferenced again in sco_sock_timeout. As a
result, the use-after-free bugs will happen. The root cause is
shown below:

    Cleanup Thread               |      Worker Thread
sco_sock_release                 |
  sco_sock_close                 |
    __sco_sock_close             |
      sco_sock_set_timer         |
        schedule_delayed_work    |
  sco_sock_kill                  |    (wait a time)
    sock_put(sk) //FREE          |  sco_sock_timeout
                                 |    sock_hold(sk) //USE

The KASAN report triggered by POC is shown below:

[   95.890016] ==================================================================
[   95.890496] BUG: KASAN: slab-use-after-free in sco_sock_timeout+0x5e/0x1c0
[   95.890755] Write of size 4 at addr ffff88800c388080 by task kworker/0:0/7
...
[   95.890755] Workqueue: events sco_sock_timeout
[   95.890755] Call Trace:
[   95.890755]  <TASK>
[   95.890755]  dump_stack_lvl+0x45/0x110
[   95.890755]  print_address_description+0x78/0x390
[   95.890755]  print_report+0x11b/0x250
[   95.890755]  ? __virt_addr_valid+0xbe/0xf0
[   95.890755]  ? sco_sock_timeout+0x5e/0x1c0
[   95.890755]  kasan_report+0x139/0x170
[   95.890755]  ? update_load_avg+0xe5/0x9f0
[   95.890755]  ? sco_sock_timeout+0x5e/0x1c0
[   95.890755]  kasan_check_range+0x2c3/0x2e0
[   95.890755]  sco_sock_timeout+0x5e/0x1c0
[   95.890755]  process_one_work+0x561/0xc50
[   95.890755]  worker_thread+0xab2/0x13c0
[   95.890755]  ? pr_cont_work+0x490/0x490
[   95.890755]  kthread+0x279/0x300
[   95.890755]  ? pr_cont_work+0x490/0x490
[   95.890755]  ? kthread_blkcg+0xa0/0xa0
[   95.890755]  ret_from_fork+0x34/0x60
[   95.890755]  ? kthread_blkcg+0xa0/0xa0
[   95.890755]  ret_from_fork_asm+0x11/0x20
[   95.890755]  </TASK>
[   95.890755]
[   95.890755] Allocated by task 506:
[   95.890755]  kasan_save_track+0x3f/0x70
[   95.890755]  __kasan_kmalloc+0x86/0x90
[   95.890755]  __kmalloc+0x17f/0x360
[   95.890755]  sk_prot_alloc+0xe1/0x1a0
[   95.890755]  sk_alloc+0x31/0x4e0
[   95.890755]  bt_sock_alloc+0x2b/0x2a0
[   95.890755]  sco_sock_create+0xad/0x320
[   95.890755]  bt_sock_create+0x145/0x320
[   95.890755]  __sock_create+0x2e1/0x650
[   95.890755]  __sys_socket+0xd0/0x280
[   95.890755]  __x64_sys_socket+0x75/0x80
[   95.890755]  do_syscall_64+0xc4/0x1b0
[   95.890755]  entry_SYSCALL_64_after_hwframe+0x67/0x6f
[   95.890755]
[   95.890755] Freed by task 506:
[   95.890755]  kasan_save_track+0x3f/0x70
[   95.890755]  kasan_save_free_info+0x40/0x50
[   95.890755]  poison_slab_object+0x118/0x180
[   95.890755]  __kasan_slab_free+0x12/0x30
[   95.890755]  kfree+0xb2/0x240
[   95.890755]  __sk_destruct+0x317/0x410
[   95.890755]  sco_sock_release+0x232/0x280
[   95.890755]  sock_close+0xb2/0x210
[   95.890755]  __fput+0x37f/0x770
[   95.890755]  task_work_run+0x1ae/0x210
[   95.890755]  get_signal+0xe17/0xf70
[   95.890755]  arch_do_signal_or_restart+0x3f/0x520
[   95.890755]  syscall_exit_to_user_mode+0x55/0x120
[   95.890755]  do_syscall_64+0xd1/0x1b0
[   95.890755]  entry_SYSCALL_64_after_hwframe+0x67/0x6f
[   95.890755]
[   95.890755] The buggy address belongs to the object at ffff88800c388000
[   95.890755]  which belongs to the cache kmalloc-1k of size 1024
[   95.890755] The buggy address is located 128 bytes inside of
[   95.890755]  freed 1024-byte region [ffff88800c388000, ffff88800c388400)
[   95.890755]
[   95.890755] The buggy address belongs to the physical page:
[   95.890755] page: refcount:1 mapcount:0 mapping:0000000000000000 index:0xffff88800c38a800 pfn:0xc388
[   95.890755] head: order:3 entire_mapcount:0 nr_pages_mapped:0 pincount:0
[   95.890755] ano
---truncated---

## References
- http://www.openwall.com/lists/oss-security/2024/11/29/1
- http://www.openwall.com/lists/oss-security/2024/11/30/1
- http://www.openwall.com/lists/oss-security/2024/11/30/2
- https://git.kernel.org/stable/c/012363cb1bec5f33a7b94629ab2c1086f30280f2
- https://git.kernel.org/stable/c/1b33d55fb7355e27f8c82cd4ecd560f162469249
- https://git.kernel.org/stable/c/3212afd00e3cda790fd0583cb3eaef8f9575a014
- https://git.kernel.org/stable/c/33a6e92161a78c1073d90e27abe28d746feb0a53
- https://git.kernel.org/stable/c/483bc08181827fc475643272ffb69c533007e546
- https://git.kernel.org/stable/c/50c2037fc28df870ef29d9728c770c8955d32178
- https://git.kernel.org/stable/c/6a18eeb1b3bbc67c20d9609c31dca6a69b4bcde5
- https://git.kernel.org/stable/c/bfab2c1f7940a232cd519e82fff137e308abfd93
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DW2MIOIMOFUSNLHLRYX23AFR36BMKD65/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OTB4HWU2PTVW5NEYHHLOCXDKG3PYA534/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27398.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27398
- https://security.netapp.com/advisory/ntap-20240912-0012/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
