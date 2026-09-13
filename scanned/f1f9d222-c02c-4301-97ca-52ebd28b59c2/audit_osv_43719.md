# [H] net/sched: act_ct: fix sk_buff leak when the header checks reject a packet

## Summary
Severity: High
Advisory: CVE-2026-74621
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74621
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.8.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_ct: fix sk_buff leak when the header checks reject a packet

tcf_ct_handle_fragments() runs its header sanity checks before handing
anything to the defragmentation engine:

	if (family == NFPROTO_IPV4)
		err = tcf_ct_ipv4_is_fragment(skb, &frag);
	else
		err = tcf_ct_ipv6_is_fragment(skb, &frag);
	if (err || !frag)
		return err;

tcf_ct_ipv4_is_fragment() returns -EINVAL or -ENOMEM;
tcf_ct_ipv6_is_fragment() adds -EPROTO when ipv6_find_hdr() fails. None of
them frees or queues the skb, so on that path the caller still owns it.

tcf_ct_act() however funnels every non-zero return into the
ownership-transfer exit:

	err = tcf_ct_handle_fragments(net, skb, family, p->zone, &defrag);
	if (err)
		goto out_frag;
	...
out_frag:
	if (err != -EINPROGRESS)
		tcf_action_inc_drop_qstats(&c->common);
	return TC_ACT_CONSUMED;

TC_ACT_CONSUMED means the action took ownership of the skb, so no caller
frees it - sch_handle_ingress(), sch_handle_egress() and
tcf_qevent_handle() all deliberately skip the free for that verdict. The
skb is therefore orphaned: one sk_buff plus its data buffer is leaked per
malformed packet, unbounded. Note the drop counter is already incremented
for these errors, so the statistics claim a drop that never happens.

Three different ownership states reach out_frag: today - the skb may be
queued by the defrag engine (-EINPROGRESS), already freed by
nf_ct_handle_fragments(), or still owned by us. Tell the caller which of
those it is, and free the packet ourselves in the last case, which
restores the TC_ACT_SHOT behaviour that predated the Fixes: commit.

Reproduced on v7.2-rc6 with a 54-byte frame carrying a 40-byte IPv6
header with nexthdr = 0 (hop-by-hop) and nothing after it, on a
clsact ingress chain with "action ct". kmemleak reports one leaked
232-byte skbuff_head_cache object plus its 704-byte data buffer per
packet; with this patch it reports none.

## References
- https://git.kernel.org/stable/c/23e97d594ddd0153020c506d5041048fbde1beb4
- https://git.kernel.org/stable/c/439d3e404f9d5e515911cc8132cde198b337c19e
- https://git.kernel.org/stable/c/47d99828591d0fe8be4b9c8992ff3b8e47968db9
- https://git.kernel.org/stable/c/737873a59905a54ca0d2d127ef882f3f88bf4379
- https://git.kernel.org/stable/c/8a7ed561671aa6a911a2de99e59ef670a4d0b1df
- https://git.kernel.org/stable/c/b47bb899e04b5407c5a63fe88d4b6676586a6e84
- https://git.kernel.org/stable/c/b5dbecc2016e1692fd1c2532af9c41ba729cb747
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74621.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74621
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
