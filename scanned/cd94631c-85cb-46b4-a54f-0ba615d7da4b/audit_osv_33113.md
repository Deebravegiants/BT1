# [C] net, hsr: reject HSR frame if skb can't hold tag

## Summary
Severity: Critical
Advisory: CVE-2025-39703
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39703
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.241, >=5.11.0 <5.15.190, >=5.13.0 <6.1.149, >=5.16.0 <6.6.103, >=6.2.0 <6.12.44, >=6.7.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net, hsr: reject HSR frame if skb can't hold tag

Receiving HSR frame with insufficient space to hold HSR tag in the skb
can result in a crash (kernel BUG):

[   45.390915] skbuff: skb_under_panic: text:ffffffff86f32cac len:26 put:14 head:ffff888042418000 data:ffff888042417ff4 tail:0xe end:0x180 dev:bridge_slave_1
[   45.392559] ------------[ cut here ]------------
[   45.392912] kernel BUG at net/core/skbuff.c:211!
[   45.393276] Oops: invalid opcode: 0000 [#1] SMP DEBUG_PAGEALLOC KASAN NOPTI
[   45.393809] CPU: 1 UID: 0 PID: 2496 Comm: reproducer Not tainted 6.15.0 #12 PREEMPT(undef)
[   45.394433] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.16.3-0-ga6ed6b701f0a-prebuilt.qemu.org 04/01/2014
[   45.395273] RIP: 0010:skb_panic+0x15b/0x1d0

<snip registers, remove unreliable trace>

[   45.402911] Call Trace:
[   45.403105]  <IRQ>
[   45.404470]  skb_push+0xcd/0xf0
[   45.404726]  br_dev_queue_push_xmit+0x7c/0x6c0
[   45.406513]  br_forward_finish+0x128/0x260
[   45.408483]  __br_forward+0x42d/0x590
[   45.409464]  maybe_deliver+0x2eb/0x420
[   45.409763]  br_flood+0x174/0x4a0
[   45.410030]  br_handle_frame_finish+0xc7c/0x1bc0
[   45.411618]  br_handle_frame+0xac3/0x1230
[   45.413674]  __netif_receive_skb_core.constprop.0+0x808/0x3df0
[   45.422966]  __netif_receive_skb_one_core+0xb4/0x1f0
[   45.424478]  __netif_receive_skb+0x22/0x170
[   45.424806]  process_backlog+0x242/0x6d0
[   45.425116]  __napi_poll+0xbb/0x630
[   45.425394]  net_rx_action+0x4d1/0xcc0
[   45.427613]  handle_softirqs+0x1a4/0x580
[   45.427926]  do_softirq+0x74/0x90
[   45.428196]  </IRQ>

This issue was found by syzkaller.

The panic happens in br_dev_queue_push_xmit() once it receives a
corrupted skb with ETH header already pushed in linear data. When it
attempts the skb_push() call, there's not enough headroom and
skb_push() panics.

The corrupted skb is put on the queue by HSR layer, which makes a
sequence of unintended transformations when it receives a specific
corrupted HSR frame (with incomplete TAG).

Fix it by dropping and consuming frames that are not long enough to
contain both ethernet and hsr headers.

Alternative fix would be to check for enough headroom before skb_push()
in br_dev_queue_push_xmit().

In the reproducer, this is injected via AF_PACKET, but I don't easily
see why it couldn't be sent over the wire from adjacent network.

Further Details:

In the reproducer, the following network interface chain is set up:

┌────────────────┐   ┌────────────────┐
│ veth0_to_hsr   ├───┤  hsr_slave0    ┼───┐
└────────────────┘   └────────────────┘   │
                                          │ ┌──────┐
                                          ├─┤ hsr0 ├───┐
                                          │ └──────┘   │
┌────────────────┐   ┌────────────────┐   │            │┌────────┐
│ veth1_to_hsr   ┼───┤  hsr_slave1    ├───┘            └┤        │
└────────────────┘   └────────────────┘                ┌┼ bridge │
                                                       ││        │
                                                       │└────────┘
                                                       │
                                        ┌───────┐      │
                                        │  ...  ├──────┘
                                        └───────┘

To trigger the events leading up to crash, reproducer sends a corrupted
HSR fr
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/3ae272ab523dd6bdc26e879027ed79feac9dd1b3
- https://git.kernel.org/stable/c/61009439e4bd8d74e705ee15940760321be91d8a
- https://git.kernel.org/stable/c/7af76e9d18a9fd6f8611b3313c86c190f9b6a5a7
- https://git.kernel.org/stable/c/8d9bc4a375a1ba05f7dfa0407de8e510ab9bd14d
- https://git.kernel.org/stable/c/acd69b597bd3f76d3b3d322b84082226c00eeaa4
- https://git.kernel.org/stable/c/b117c41b00902c1a7e24347c405cb82504aeae0b
- https://git.kernel.org/stable/c/b640188b8a6690e685939053c7efdbc7818b5f4e
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39703.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39703
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
