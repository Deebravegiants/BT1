# [H] netfilter: bridge: fix stale prevhdr pointer in br_ip6_fragment()

## Summary
Severity: High
Advisory: CVE-2026-64554
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64554
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bridge: fix stale prevhdr pointer in br_ip6_fragment()

br_ip6_fragment() gets prevhdr, a pointer into the skb head, from
ip6_find_1stfragopt(), then calls skb_checksum_help().  For a cloned skb
skb_checksum_help() reallocates the head via pskb_expand_head(), leaving
prevhdr dangling.  It is later dereferenced in ip6_frag_next(), causing a
use-after-free write.

Save prevhdr's offset before skb_checksum_help() and recompute it after,
like commit ef0efcd3bd3f ("ipv6: Fix dangling pointer when ipv6
fragment").

  BUG: KASAN: slab-use-after-free in ip6_frag_next (net/ipv6/ip6_output.c:857)
  Write of size 1 at addr ffff888013ff5016 by task exploit/141
  Call Trace:
   ...
   kasan_report (mm/kasan/report.c:595)
   ip6_frag_next (net/ipv6/ip6_output.c:857)
   br_ip6_fragment (net/ipv6/netfilter.c:212)
   nf_ct_bridge_post (net/bridge/netfilter/nf_conntrack_bridge.c:407)
   nf_hook_slow (net/netfilter/core.c:619)
   br_forward_finish (net/bridge/br_forward.c:66)
   __br_forward (net/bridge/br_forward.c:115)
   maybe_deliver (net/bridge/br_forward.c:191)
   br_flood (net/bridge/br_forward.c:245)
   br_handle_frame_finish (net/bridge/br_input.c:229)
   br_handle_frame (net/bridge/br_input.c:442)
   ...
   packet_sendmsg (net/packet/af_packet.c:3114)
   ...
   do_syscall_64 (arch/x86/entry/syscall_64.c:94)
   entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:121)
  Kernel panic - not syncing: Fatal exception in interrupt

## References
- https://git.kernel.org/stable/c/00c06ef8c018493943891a7d0ca82b71b24f3180
- https://git.kernel.org/stable/c/1c4f67c89fd27c4df4c70b135c2c59627698b3c0
- https://git.kernel.org/stable/c/2731efa6364e47934c96eb69e01ea131e8af8030
- https://git.kernel.org/stable/c/4ac981a8b7ce7aec99a52d08f8a8953e8e120067
- https://git.kernel.org/stable/c/86f3ce81dd2b4b0aa2c3016c989a943e4b1b643d
- https://git.kernel.org/stable/c/8c10778ec674b67a07ea042fcba64270f3f38a5a
- https://git.kernel.org/stable/c/c141f69d0a0fb16964dbc293650047e69bda8af7
- https://git.kernel.org/stable/c/f2e6596d10783557aeb9668da2a3b4d19deb2001
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64554
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
