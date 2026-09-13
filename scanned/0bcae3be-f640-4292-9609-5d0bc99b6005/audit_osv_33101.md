# [H] net/sched: Fix backlog accounting in qdisc_dequeue_internal

## Summary
Severity: High
Advisory: CVE-2025-39677
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39677
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: Fix backlog accounting in qdisc_dequeue_internal

This issue applies for the following qdiscs: hhf, fq, fq_codel, and
fq_pie, and occurs in their change handlers when adjusting to the new
limit. The problem is the following in the values passed to the
subsequent qdisc_tree_reduce_backlog call given a tbf parent:

   When the tbf parent runs out of tokens, skbs of these qdiscs will
   be placed in gso_skb. Their peek handlers are qdisc_peek_dequeued,
   which accounts for both qlen and backlog. However, in the case of
   qdisc_dequeue_internal, ONLY qlen is accounted for when pulling
   from gso_skb. This means that these qdiscs are missing a
   qdisc_qstats_backlog_dec when dropping packets to satisfy the
   new limit in their change handlers.

   One can observe this issue with the following (with tc patched to
   support a limit of 0):

   export TARGET=fq
   tc qdisc del dev lo root
   tc qdisc add dev lo root handle 1: tbf rate 8bit burst 100b latency 1ms
   tc qdisc replace dev lo handle 3: parent 1:1 $TARGET limit 1000
   echo ''; echo 'add child'; tc -s -d qdisc show dev lo
   ping -I lo -f -c2 -s32 -W0.001 127.0.0.1 2>&1 >/dev/null
   echo ''; echo 'after ping'; tc -s -d qdisc show dev lo
   tc qdisc change dev lo handle 3: parent 1:1 $TARGET limit 0
   echo ''; echo 'after limit drop'; tc -s -d qdisc show dev lo
   tc qdisc replace dev lo handle 2: parent 1:1 sfq
   echo ''; echo 'post graft'; tc -s -d qdisc show dev lo

   The second to last show command shows 0 packets but a positive
   number (74) of backlog bytes. The problem becomes clearer in the
   last show command, where qdisc_purge_queue triggers
   qdisc_tree_reduce_backlog with the positive backlog and causes an
   underflow in the tbf parent's backlog (4096 Mb instead of 0).

To fix this issue, the codepath for all clients of qdisc_dequeue_internal
has been simplified: codel, pie, hhf, fq, fq_pie, and fq_codel.
qdisc_dequeue_internal handles the backlog adjustments for all cases that
do not directly use the dequeue handler.

The old fq_codel_change limit adjustment loop accumulated the arguments to
the subsequent qdisc_tree_reduce_backlog call through the cstats field.
However, this is confusing and error prone as fq_codel_dequeue could also
potentially mutate this field (which qdisc_dequeue_internal calls in the
non gso_skb case), so we have unified the code here with other qdiscs.

## References
- https://git.kernel.org/stable/c/52bf272636bda69587952b35ae97690b8dc89941
- https://git.kernel.org/stable/c/a225f44d84b8900d679c5f5a9ea46fe9c0cc7802
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39677.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39677
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
