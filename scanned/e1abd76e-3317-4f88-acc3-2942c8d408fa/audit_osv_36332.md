# [H] gue: Fix skb memleak with inner IP protocol 0.

## Summary
Severity: High
Advisory: CVE-2026-23095
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23095
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

gue: Fix skb memleak with inner IP protocol 0.

syzbot reported skb memleak below. [0]

The repro generated a GUE packet with its inner protocol 0.

gue_udp_recv() returns -guehdr->proto_ctype for "resubmit"
in ip_protocol_deliver_rcu(), but this only works with
non-zero protocol number.

Let's drop such packets.

Note that 0 is a valid number (IPv6 Hop-by-Hop Option).

I think it is not practical to encap HOPOPT in GUE, so once
someone starts to complain, we could pass down a resubmit
flag pointer to distinguish two zeros from the upper layer:

  * no error
  * resubmit HOPOPT

[0]
BUG: memory leak
unreferenced object 0xffff888109695a00 (size 240):
  comm "syz.0.17", pid 6088, jiffies 4294943096
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 40 c2 10 81 88 ff ff 00 00 00 00 00 00 00 00  .@..............
  backtrace (crc a84b336f):
    kmemleak_alloc_recursive include/linux/kmemleak.h:44 [inline]
    slab_post_alloc_hook mm/slub.c:4958 [inline]
    slab_alloc_node mm/slub.c:5263 [inline]
    kmem_cache_alloc_noprof+0x3b4/0x590 mm/slub.c:5270
    __build_skb+0x23/0x60 net/core/skbuff.c:474
    build_skb+0x20/0x190 net/core/skbuff.c:490
    __tun_build_skb drivers/net/tun.c:1541 [inline]
    tun_build_skb+0x4a1/0xa40 drivers/net/tun.c:1636
    tun_get_user+0xc12/0x2030 drivers/net/tun.c:1770
    tun_chr_write_iter+0x71/0x120 drivers/net/tun.c:1999
    new_sync_write fs/read_write.c:593 [inline]
    vfs_write+0x45d/0x710 fs/read_write.c:686
    ksys_write+0xa7/0x170 fs/read_write.c:738
    do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]
    do_syscall_64+0xa4/0xf80 arch/x86/entry/syscall_64.c:94
    entry_SYSCALL_64_after_hwframe+0x77/0x7f

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/380a82d36e37db49fd41ecc378c22fd29392e96a
- https://git.kernel.org/stable/c/536f5bbc322eb1e175bdd1ced22b236a951c4d8f
- https://git.kernel.org/stable/c/5437a279804ced8088cabb945dba88a26d828f8c
- https://git.kernel.org/stable/c/886f186328b718400dbf79e1bc8cbcbd710ab766
- https://git.kernel.org/stable/c/9a56796ad258786d3624eef5aefba394fc9bdded
- https://git.kernel.org/stable/c/ce569b389a5c78d64788a5ea94560e17fa574b35
- https://git.kernel.org/stable/c/f87b9b7a618c82e7465e872eb10e14c803871892
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23095.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23095
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
