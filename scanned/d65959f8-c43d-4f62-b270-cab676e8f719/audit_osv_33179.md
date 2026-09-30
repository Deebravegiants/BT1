# [M] net/tcp: Fix socket memory leak in TCP-AO failure handling for IPv6

## Summary
Severity: Medium
Advisory: CVE-2025-39852
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39852
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tcp: Fix socket memory leak in TCP-AO failure handling for IPv6

When tcp_ao_copy_all_matching() fails in tcp_v6_syn_recv_sock() it just
exits the function. This ends up causing a memory-leak:

unreferenced object 0xffff0000281a8200 (size 2496):
  comm "softirq", pid 0, jiffies 4295174684
  hex dump (first 32 bytes):
    7f 00 00 06 7f 00 00 06 00 00 00 00 cb a8 88 13  ................
    0a 00 03 61 00 00 00 00 00 00 00 00 00 00 00 00  ...a............
  backtrace (crc 5ebdbe15):
    kmemleak_alloc+0x44/0xe0
    kmem_cache_alloc_noprof+0x248/0x470
    sk_prot_alloc+0x48/0x120
    sk_clone_lock+0x38/0x3b0
    inet_csk_clone_lock+0x34/0x150
    tcp_create_openreq_child+0x3c/0x4a8
    tcp_v6_syn_recv_sock+0x1c0/0x620
    tcp_check_req+0x588/0x790
    tcp_v6_rcv+0x5d0/0xc18
    ip6_protocol_deliver_rcu+0x2d8/0x4c0
    ip6_input_finish+0x74/0x148
    ip6_input+0x50/0x118
    ip6_sublist_rcv+0x2fc/0x3b0
    ipv6_list_rcv+0x114/0x170
    __netif_receive_skb_list_core+0x16c/0x200
    netif_receive_skb_list_internal+0x1f0/0x2d0

This is because in tcp_v6_syn_recv_sock (and the IPv4 counterpart), when
exiting upon error, inet_csk_prepare_forced_close() and tcp_done() need
to be called. They make sure the newsk will end up being correctly
free'd.

tcp_v4_syn_recv_sock() makes this very clear by having the put_and_exit
label that takes care of things. So, this patch here makes sure
tcp_v4_syn_recv_sock and tcp_v6_syn_recv_sock have similar
error-handling and thus fixes the leak for TCP-AO.

## References
- https://git.kernel.org/stable/c/3d2b356d994a8801acb397cafd28b13672c37ab5
- https://git.kernel.org/stable/c/46d33c878fc0b3d7570366b2c9912395b3f4e701
- https://git.kernel.org/stable/c/fa390321aba0a54d0f7ae95ee4ecde1358bb9234
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39852.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39852
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
