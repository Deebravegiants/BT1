# [H] netfilter: br_netfilter: do not check confirmed bit in br_nf_local_in() after confirm

## Summary
Severity: High
Advisory: CVE-2025-39894
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39894
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.8.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: br_netfilter: do not check confirmed bit in br_nf_local_in() after confirm

When send a broadcast packet to a tap device, which was added to a bridge,
br_nf_local_in() is called to confirm the conntrack. If another conntrack
with the same hash value is added to the hash table, which can be
triggered by a normal packet to a non-bridge device, the below warning
may happen.

  ------------[ cut here ]------------
  WARNING: CPU: 1 PID: 96 at net/bridge/br_netfilter_hooks.c:632 br_nf_local_in+0x168/0x200
  CPU: 1 UID: 0 PID: 96 Comm: tap_send Not tainted 6.17.0-rc2-dirty #44 PREEMPT(voluntary)
  RIP: 0010:br_nf_local_in+0x168/0x200
  Call Trace:
   <TASK>
   nf_hook_slow+0x3e/0xf0
   br_pass_frame_up+0x103/0x180
   br_handle_frame_finish+0x2de/0x5b0
   br_nf_hook_thresh+0xc0/0x120
   br_nf_pre_routing_finish+0x168/0x3a0
   br_nf_pre_routing+0x237/0x5e0
   br_handle_frame+0x1ec/0x3c0
   __netif_receive_skb_core+0x225/0x1210
   __netif_receive_skb_one_core+0x37/0xa0
   netif_receive_skb+0x36/0x160
   tun_get_user+0xa54/0x10c0
   tun_chr_write_iter+0x65/0xb0
   vfs_write+0x305/0x410
   ksys_write+0x60/0xd0
   do_syscall_64+0xa4/0x260
   entry_SYSCALL_64_after_hwframe+0x77/0x7f
   </TASK>
  ---[ end trace 0000000000000000 ]---

To solve the hash conflict, nf_ct_resolve_clash() try to merge the
conntracks, and update skb->_nfct. However, br_nf_local_in() still use the
old ct from local variable 'nfct' after confirm(), which leads to this
warning.

If confirm() does not insert the conntrack entry and return NF_DROP, the
warning may also occur. There is no need to reserve the WARN_ON_ONCE, just
remove it.

## References
- https://git.kernel.org/stable/c/479a54ab92087318514c82428a87af2d7af1a576
- https://git.kernel.org/stable/c/50db11e2bbb635e38e3dd096215580d6adb41fb0
- https://git.kernel.org/stable/c/a74abcf0f09f59daeecf7a3ba9c1d690808b0afe
- https://git.kernel.org/stable/c/c47ca77fee9071aa543bae592dd2a384f895c8b6
- https://git.kernel.org/stable/c/ccbad4803225eafe0175d3cb19f0d8d73b504a94
- https://git.kernel.org/stable/c/d00c8b0daf56012f69075e3377da67878c775e4c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39894.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39894
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
