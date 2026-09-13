# [H] bpf, test_run: Fix use-after-free issue in eth_skb_pkt_type()

## Summary
Severity: High
Advisory: CVE-2025-21867
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21867
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, test_run: Fix use-after-free issue in eth_skb_pkt_type()

KMSAN reported a use-after-free issue in eth_skb_pkt_type()[1]. The
cause of the issue was that eth_skb_pkt_type() accessed skb's data
that didn't contain an Ethernet header. This occurs when
bpf_prog_test_run_xdp() passes an invalid value as the user_data
argument to bpf_test_init().

Fix this by returning an error when user_data is less than ETH_HLEN in
bpf_test_init(). Additionally, remove the check for "if (user_size >
size)" as it is unnecessary.

[1]
BUG: KMSAN: use-after-free in eth_skb_pkt_type include/linux/etherdevice.h:627 [inline]
BUG: KMSAN: use-after-free in eth_type_trans+0x4ee/0x980 net/ethernet/eth.c:165
 eth_skb_pkt_type include/linux/etherdevice.h:627 [inline]
 eth_type_trans+0x4ee/0x980 net/ethernet/eth.c:165
 __xdp_build_skb_from_frame+0x5a8/0xa50 net/core/xdp.c:635
 xdp_recv_frames net/bpf/test_run.c:272 [inline]
 xdp_test_run_batch net/bpf/test_run.c:361 [inline]
 bpf_test_run_xdp_live+0x2954/0x3330 net/bpf/test_run.c:390
 bpf_prog_test_run_xdp+0x148e/0x1b10 net/bpf/test_run.c:1318
 bpf_prog_test_run+0x5b7/0xa30 kernel/bpf/syscall.c:4371
 __sys_bpf+0x6a6/0xe20 kernel/bpf/syscall.c:5777
 __do_sys_bpf kernel/bpf/syscall.c:5866 [inline]
 __se_sys_bpf kernel/bpf/syscall.c:5864 [inline]
 __x64_sys_bpf+0xa4/0xf0 kernel/bpf/syscall.c:5864
 x64_sys_call+0x2ea0/0x3d90 arch/x86/include/generated/asm/syscalls_64.h:322
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0xd9/0x1d0 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Uninit was created at:
 free_pages_prepare mm/page_alloc.c:1056 [inline]
 free_unref_page+0x156/0x1320 mm/page_alloc.c:2657
 __free_pages+0xa3/0x1b0 mm/page_alloc.c:4838
 bpf_ringbuf_free kernel/bpf/ringbuf.c:226 [inline]
 ringbuf_map_free+0xff/0x1e0 kernel/bpf/ringbuf.c:235
 bpf_map_free kernel/bpf/syscall.c:838 [inline]
 bpf_map_free_deferred+0x17c/0x310 kernel/bpf/syscall.c:862
 process_one_work kernel/workqueue.c:3229 [inline]
 process_scheduled_works+0xa2b/0x1b60 kernel/workqueue.c:3310
 worker_thread+0xedf/0x1550 kernel/workqueue.c:3391
 kthread+0x535/0x6b0 kernel/kthread.c:389
 ret_from_fork+0x6e/0x90 arch/x86/kernel/process.c:147
 ret_from_fork_asm+0x1a/0x30 arch/x86/entry/entry_64.S:244

CPU: 1 UID: 0 PID: 17276 Comm: syz.1.16450 Not tainted 6.12.0-05490-g9bb88c659673 #8
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-3.fc41 04/01/2014

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/1a9e1284e87d59b1303b69d1808d310821d6e5f7
- https://git.kernel.org/stable/c/6b3d638ca897e099fa99bd6d02189d3176f80a47
- https://git.kernel.org/stable/c/972bafed67ca73ad9a56448384281eb5fd5c0ba3
- https://git.kernel.org/stable/c/d56d8a23d95100b65f40438639dd82db2af81c11
- https://git.kernel.org/stable/c/f615fccfc689cb48977d275ac2e391297b52392b
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21867.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
