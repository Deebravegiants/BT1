# [C] net/sched: cls_api: Handle TC_ACT_CONSUMED in tcf_qevent_handle

## Summary
Severity: Critical
Advisory: CVE-2026-64530
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-26
Source: https://osv.dev/vulnerability/CVE-2026-64530
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.8.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_api: Handle TC_ACT_CONSUMED in tcf_qevent_handle

tcf_classify() can return TC_ACT_CONSUMED while the skb is held by the
defragmentation engine (e.g. act_ct on out-of-order fragments). When
that happens the skb is no longer owned by the caller and must not be
touched again.

tcf_qevent_handle() did not handle TC_ACT_CONSUMED: it fell through the
switch and returned the skb to the caller as if classification had
passed. The only qdisc that wires up qevents today is RED, via three call sites
(qe_mark on RED_PROB_MARK/HARD_MARK, qe_early_drop on congestion_drop)
red_enqueue() was continuing to operate on an skb it no longer owns  in this
case -- enqueueing it, dropping it, or updating statistics. Resulting in a UAF.

  tc qdisc add dev eth0 root handle 1: red ... qevent early_drop block 10
  tc filter add block 10 ... action ct

  (with ct defrag enabled and traffic that produces out-of-order
  fragments, e.g. a fragmented UDP stream)

Handle TC_ACT_CONSUMED in tcf_qevent_handle() the same way the ingress
and egress fast paths do: treat it as stolen and return NULL without
touching the skb. Unlike the TC_ACT_STOLEN case, the skb must not be
dropped/freed here, as it is no longer owned by us.

## References
- https://git.kernel.org/stable/c/2140c2f3f2e7b066e1ae616ede8856cafd8015e9
- https://git.kernel.org/stable/c/447d493034a9cf7bf13a2abac86d0573d907ec2f
- https://git.kernel.org/stable/c/5ed3d6f85991656667059d3fa5a1d683ac58c447
- https://git.kernel.org/stable/c/a8a02897f2b479127db261de05cbf0c28b98d159
- https://git.kernel.org/stable/c/e1270e69dcf2c3512c453484178f2e9dc0db3f05
- https://git.kernel.org/stable/c/e28aedab9488343924d227b5a896faed67ce84d5
- https://git.kernel.org/stable/c/f42e8134a3a1074b834a574d404352f867ba994a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64530.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64530
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
