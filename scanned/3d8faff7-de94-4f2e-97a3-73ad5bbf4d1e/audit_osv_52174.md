# [M] CVE-2021-47162

## Summary
Severity: Medium
Advisory: CVE-2021-47162
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47162
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: skb_linearize the head skb when reassembling msgs

It's not a good idea to append the frag skb to a skb's frag_list if
the frag_list already has skbs from elsewhere, such as this skb was
created by pskb_copy() where the frag_list was cloned (all the skbs
in it were skb_get'ed) and shared by multiple skbs.

However, the new appended frag skb should have been only seen by the
current skb. Otherwise, it will cause use after free crashes as this
appended frag skb are seen by multiple skbs but it only got skb_get
called once.

The same thing happens with a skb updated by pskb_may_pull() with a
skb_cloned skb. Li Shuang has reported quite a few crashes caused
by this when doing testing over macvlan devices:

  [] kernel BUG at net/core/skbuff.c:1970!
  [] Call Trace:
  []  skb_clone+0x4d/0xb0
  []  macvlan_broadcast+0xd8/0x160 [macvlan]
  []  macvlan_process_broadcast+0x148/0x150 [macvlan]
  []  process_one_work+0x1a7/0x360
  []  worker_thread+0x30/0x390

  [] kernel BUG at mm/usercopy.c:102!
  [] Call Trace:
  []  __check_heap_object+0xd3/0x100
  []  __check_object_size+0xff/0x16b
  []  simple_copy_to_iter+0x1c/0x30
  []  __skb_datagram_iter+0x7d/0x310
  []  __skb_datagram_iter+0x2a5/0x310
  []  skb_copy_datagram_iter+0x3b/0x90
  []  tipc_recvmsg+0x14a/0x3a0 [tipc]
  []  ____sys_recvmsg+0x91/0x150
  []  ___sys_recvmsg+0x7b/0xc0

  [] kernel BUG at mm/slub.c:305!
  [] Call Trace:
  []  <IRQ>
  []  kmem_cache_free+0x3ff/0x400
  []  __netif_receive_skb_core+0x12c/0xc40
  []  ? kmem_cache_alloc+0x12e/0x270
  []  netif_receive_skb_internal+0x3d/0xb0
  []  ? get_rx_page_info+0x8e/0xa0 [be2net]
  []  be_poll+0x6ef/0xd00 [be2net]
  []  ? irq_exit+0x4f/0x100
  []  net_rx_action+0x149/0x3b0

  ...

This patch is to fix it by linearizing the head skb if it has frag_list
set in tipc_buf_append(). Note that we choose to do this before calling
skb_unshare(), as __skb_linearize() will avoid skb_copy(). Also, we can
not just drop the frag_list either as the early time.

## References
- https://git.kernel.org/stable/c/5489f30bb78ff0dafb4229a69632afc2ba20765c
- https://git.kernel.org/stable/c/64d17ec9f1ded042c4b188d15734f33486ed9966
- https://git.kernel.org/stable/c/6da24cfc83ba4f97ea44fc7ae9999a006101755c
- https://git.kernel.org/stable/c/ace300eecbccaa698e2b472843c74a5f33f7dce8
- https://git.kernel.org/stable/c/b2c8d28c34b3070407cb1741f9ba3f15d0284b8b
- https://git.kernel.org/stable/c/b7df21cf1b79ab7026f545e7bf837bd5750ac026
- https://git.kernel.org/stable/c/436d650d374329a591c30339a91fa5078052ed1e
- https://git.kernel.org/stable/c/4b1761898861117c97066aea6c58f68a7787f0bf
