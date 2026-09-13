# [H] block: fix request.queuelist usage in flush

## Summary
Severity: High
Advisory: CVE-2024-40925
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40925
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: fix request.queuelist usage in flush

Friedrich Weber reported a kernel crash problem and bisected to commit
81ada09cc25e ("blk-flush: reuse rq queuelist in flush state machine").

The root cause is that we use "list_move_tail(&rq->queuelist, pending)"
in the PREFLUSH/POSTFLUSH sequences. But rq->queuelist.next == xxx since
it's popped out from plug->cached_rq in __blk_mq_alloc_requests_batch().
We don't initialize its queuelist just for this first request, although
the queuelist of all later popped requests will be initialized.

Fix it by changing to use "list_add_tail(&rq->queuelist, pending)" so
rq->queuelist doesn't need to be initialized. It should be ok since rq
can't be on any list when PREFLUSH or POSTFLUSH, has no move actually.

Please note the commit 81ada09cc25e ("blk-flush: reuse rq queuelist in
flush state machine") also has another requirement that no drivers would
touch rq->queuelist after blk_mq_end_request() since we will reuse it to
add rq to the post-flush pending list in POSTFLUSH. If this is not true,
we will have to revert that commit IMHO.

This updated version adds "list_del_init(&rq->queuelist)" in flush rq
callback since the dm layer may submit request of a weird invalid format
(REQ_FSEQ_PREFLUSH | REQ_FSEQ_POSTFLUSH), which causes double list_add
if without this "list_del_init(&rq->queuelist)". The weird invalid format
problem should be fixed in dm layer.

## References
- https://git.kernel.org/stable/c/87907bd69721a8506618a954d41a1de3040e88aa
- https://git.kernel.org/stable/c/d0321c812d89c5910d8da8e4b10c891c6b96ff70
- https://git.kernel.org/stable/c/fe1e395563ccb051e9dbd8fa99859f5caaad2e71
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40925.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
