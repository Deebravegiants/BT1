# [H] net: bridge: xmit: make sure we have at least eth header len bytes

## Summary
Severity: High
Advisory: CVE-2024-38538
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38538
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: xmit: make sure we have at least eth header len bytes

syzbot triggered an uninit value[1] error in bridge device's xmit path
by sending a short (less than ETH_HLEN bytes) skb. To fix it check if
we can actually pull that amount instead of assuming.

Tested with dropwatch:
 drop at: br_dev_xmit+0xb93/0x12d0 [bridge] (0xffffffffc06739b3)
 origin: software
 timestamp: Mon May 13 11:31:53 2024 778214037 nsec
 protocol: 0x88a8
 length: 2
 original length: 2
 drop reason: PKT_TOO_SMALL

[1]
BUG: KMSAN: uninit-value in br_dev_xmit+0x61d/0x1cb0 net/bridge/br_device.c:65
 br_dev_xmit+0x61d/0x1cb0 net/bridge/br_device.c:65
 __netdev_start_xmit include/linux/netdevice.h:4903 [inline]
 netdev_start_xmit include/linux/netdevice.h:4917 [inline]
 xmit_one net/core/dev.c:3531 [inline]
 dev_hard_start_xmit+0x247/0xa20 net/core/dev.c:3547
 __dev_queue_xmit+0x34db/0x5350 net/core/dev.c:4341
 dev_queue_xmit include/linux/netdevice.h:3091 [inline]
 __bpf_tx_skb net/core/filter.c:2136 [inline]
 __bpf_redirect_common net/core/filter.c:2180 [inline]
 __bpf_redirect+0x14a6/0x1620 net/core/filter.c:2187
 ____bpf_clone_redirect net/core/filter.c:2460 [inline]
 bpf_clone_redirect+0x328/0x470 net/core/filter.c:2432
 ___bpf_prog_run+0x13fe/0xe0f0 kernel/bpf/core.c:1997
 __bpf_prog_run512+0xb5/0xe0 kernel/bpf/core.c:2238
 bpf_dispatcher_nop_func include/linux/bpf.h:1234 [inline]
 __bpf_prog_run include/linux/filter.h:657 [inline]
 bpf_prog_run include/linux/filter.h:664 [inline]
 bpf_test_run+0x499/0xc30 net/bpf/test_run.c:425
 bpf_prog_test_run_skb+0x14ea/0x1f20 net/bpf/test_run.c:1058
 bpf_prog_test_run+0x6b7/0xad0 kernel/bpf/syscall.c:4269
 __sys_bpf+0x6aa/0xd90 kernel/bpf/syscall.c:5678
 __do_sys_bpf kernel/bpf/syscall.c:5767 [inline]
 __se_sys_bpf kernel/bpf/syscall.c:5765 [inline]
 __x64_sys_bpf+0xa0/0xe0 kernel/bpf/syscall.c:5765
 x64_sys_call+0x96b/0x3b50 arch/x86/include/generated/asm/syscalls_64.h:322
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xcf/0x1e0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

## References
- https://git.kernel.org/stable/c/1abb371147905ba250b4cc0230c4be7e90bea4d5
- https://git.kernel.org/stable/c/28126b83f86ab9cc7936029c2dff845d3dcedba2
- https://git.kernel.org/stable/c/3e01fc3c66e65d9afe98f1489047a1b2dd8741ca
- https://git.kernel.org/stable/c/5b5d669f569807c7ab07546e73c0741845a2547a
- https://git.kernel.org/stable/c/82090f94c723dab724b1c32db406091d40448a17
- https://git.kernel.org/stable/c/8bd67ebb50c0145fd2ca8681ab65eb7e8cde1afc
- https://git.kernel.org/stable/c/b2b7c43cd32080221bb233741bd6011983fe7c11
- https://git.kernel.org/stable/c/c964429ef53f42098a6545a5dabeb1441c1e821d
- https://git.kernel.org/stable/c/f482fd4ce919836a49012b2d31b00fc36e2488f2
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38538.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
