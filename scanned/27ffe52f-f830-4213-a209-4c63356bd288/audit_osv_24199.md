# [H] net/tunnel: wait until all sk_user_data reader finish before releasing the sock

## Summary
Severity: High
Advisory: CVE-2022-50405
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50405
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tunnel: wait until all sk_user_data reader finish before releasing the sock

There is a race condition in vxlan that when deleting a vxlan device
during receiving packets, there is a possibility that the sock is
released after getting vxlan_sock vs from sk_user_data. Then in
later vxlan_ecn_decapsulate(), vxlan_get_sk_family() we will got
NULL pointer dereference. e.g.

   #0 [ffffa25ec6978a38] machine_kexec at ffffffff8c669757
   #1 [ffffa25ec6978a90] __crash_kexec at ffffffff8c7c0a4d
   #2 [ffffa25ec6978b58] crash_kexec at ffffffff8c7c1c48
   #3 [ffffa25ec6978b60] oops_end at ffffffff8c627f2b
   #4 [ffffa25ec6978b80] page_fault_oops at ffffffff8c678fcb
   #5 [ffffa25ec6978bd8] exc_page_fault at ffffffff8d109542
   #6 [ffffa25ec6978c00] asm_exc_page_fault at ffffffff8d200b62
      [exception RIP: vxlan_ecn_decapsulate+0x3b]
      RIP: ffffffffc1014e7b  RSP: ffffa25ec6978cb0  RFLAGS: 00010246
      RAX: 0000000000000008  RBX: ffff8aa000888000  RCX: 0000000000000000
      RDX: 000000000000000e  RSI: ffff8a9fc7ab803e  RDI: ffff8a9fd1168700
      RBP: ffff8a9fc7ab803e   R8: 0000000000700000   R9: 00000000000010ae
      R10: ffff8a9fcb748980  R11: 0000000000000000  R12: ffff8a9fd1168700
      R13: ffff8aa000888000  R14: 00000000002a0000  R15: 00000000000010ae
      ORIG_RAX: ffffffffffffffff  CS: 0010  SS: 0018
   #7 [ffffa25ec6978ce8] vxlan_rcv at ffffffffc10189cd [vxlan]
   #8 [ffffa25ec6978d90] udp_queue_rcv_one_skb at ffffffff8cfb6507
   #9 [ffffa25ec6978dc0] udp_unicast_rcv_skb at ffffffff8cfb6e45
  #10 [ffffa25ec6978dc8] __udp4_lib_rcv at ffffffff8cfb8807
  #11 [ffffa25ec6978e20] ip_protocol_deliver_rcu at ffffffff8cf76951
  #12 [ffffa25ec6978e48] ip_local_deliver at ffffffff8cf76bde
  #13 [ffffa25ec6978ea0] __netif_receive_skb_one_core at ffffffff8cecde9b
  #14 [ffffa25ec6978ec8] process_backlog at ffffffff8cece139
  #15 [ffffa25ec6978f00] __napi_poll at ffffffff8ceced1a
  #16 [ffffa25ec6978f28] net_rx_action at ffffffff8cecf1f3
  #17 [ffffa25ec6978fa0] __softirqentry_text_start at ffffffff8d4000ca
  #18 [ffffa25ec6978ff0] do_softirq at ffffffff8c6fbdc3

Reproducer: https://github.com/Mellanox/ovs-tests/blob/master/test-ovs-vxlan-remove-tunnel-during-traffic.sh

Fix this by waiting for all sk_user_data reader to finish before
releasing the sock.

## References
- https://git.kernel.org/stable/c/303000c793f705d07b551eb7c1c27001c5b33c8d
- https://git.kernel.org/stable/c/3cf7203ca620682165706f70a1b12b5194607dce
- https://git.kernel.org/stable/c/588d0b8462f5ffed3e677e65639825b2678117ab
- https://git.kernel.org/stable/c/84e566d157cc22ad2da8bdd970495855fbf13d92
- https://git.kernel.org/stable/c/91f09a776ae335ca836ed864b8f2a9461882a280
- https://git.kernel.org/stable/c/9a6544343bba7da929d6d4a2dc44ec0f15970081
- https://git.kernel.org/stable/c/b38aa7465411795e9e744b8d94633910497fec2a
- https://git.kernel.org/stable/c/be34e79e0ae6adbf6e7e75ddaee9ad84795ab933
- https://git.kernel.org/stable/c/e8316584b0a6c61c9c407631040c22712b26e38c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50405.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
