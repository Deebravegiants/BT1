# [H] net/sched: sch_taprio: Replace direct dequeue call with peek and qdisc_dequeue_peeked

## Summary
Severity: High
Advisory: CVE-2026-72035
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72035
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_taprio: Replace direct dequeue call with peek and qdisc_dequeue_peeked

When taprio's software path peeks a non-work-conserving child qdisc, the
child stashes the peeked skb in its gso_skb; taprio_dequeue_from_txq()
then takes the packet with a direct child ->dequeue() call, which ignores
that stash, orphans the peeked skb and desyncs the child's qlen/backlog.
With a qfq child this re-enters the child on an emptied list and
dereferences NULL, panicking the kernel from softirq on ordinary egress.

Take the packet through qdisc_dequeue_peeked(), as sch_red and sch_sfb
now do. The helper returns the child's stashed skb first and is a no-op
when there is none, so a work-conserving child is unaffected and the
gated path now consumes the skb whose length was charged to the budget.

## References
- https://git.kernel.org/stable/c/17ab5f76f3899f67e5569722f334591f4b88b17b
- https://git.kernel.org/stable/c/18d580cb00c55805633bae45e90cf22ed6b8e424
- https://git.kernel.org/stable/c/2dcebbd1ad2e180fe7b98bf346ced69a872e11e6
- https://git.kernel.org/stable/c/51f8af240aed903e988755af33d7491030b50ae9
- https://git.kernel.org/stable/c/6ee5a7665a9080bcb05d703bf981a579436fd05e
- https://git.kernel.org/stable/c/e056e1dfcddca877dd46d704e8ec9860cfc9ec44
- https://git.kernel.org/stable/c/e2b7ee61989f2d39df6c2cc06f9db1aea69bdb09
- https://git.kernel.org/stable/c/f60d5c12e0551012cee5c272b0bcbcc78f7bb506
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72035.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72035
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
