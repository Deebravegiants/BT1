# [H] null_blk: fix poll request timeout handling

## Summary
Severity: High
Advisory: CVE-2023-53531
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53531
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

null_blk: fix poll request timeout handling

When doing io_uring benchmark on /dev/nullb0, it's easy to crash the
kernel if poll requests timeout triggered, as reported by David. [1]

BUG: kernel NULL pointer dereference, address: 0000000000000008
Workqueue: kblockd blk_mq_timeout_work
RIP: 0010:null_timeout_rq+0x4e/0x91
Call Trace:
 ? null_timeout_rq+0x4e/0x91
 blk_mq_handle_expired+0x31/0x4b
 bt_iter+0x68/0x84
 ? bt_tags_iter+0x81/0x81
 __sbitmap_for_each_set.constprop.0+0xb0/0xf2
 ? __blk_mq_complete_request_remote+0xf/0xf
 bt_for_each+0x46/0x64
 ? __blk_mq_complete_request_remote+0xf/0xf
 ? percpu_ref_get_many+0xc/0x2a
 blk_mq_queue_tag_busy_iter+0x14d/0x18e
 blk_mq_timeout_work+0x95/0x127
 process_one_work+0x185/0x263
 worker_thread+0x1b5/0x227

This is indeed a race problem between null_timeout_rq() and null_poll().

null_poll()				null_timeout_rq()
  spin_lock(&nq->poll_lock)
  list_splice_init(&nq->poll_list, &list)
  spin_unlock(&nq->poll_lock)

  while (!list_empty(&list))
    req = list_first_entry()
    list_del_init()
    ...
    blk_mq_add_to_batch()
    // req->rq_next = NULL
					spin_lock(&nq->poll_lock)

					// rq->queuelist->next == NULL
					list_del_init(&rq->queuelist)

					spin_unlock(&nq->poll_lock)

Fix these problems by setting requests state to MQ_RQ_COMPLETE under
nq->poll_lock protection, in which null_timeout_rq() can safely detect
this race and early return.

Note this patch just fix the kernel panic when request timeout happen.

[1] https://lore.kernel.org/all/3893581.1691785261@warthog.procyon.org.uk/

## References
- https://git.kernel.org/stable/c/5a26e45edb4690d58406178b5a9ea4c6dcf2c105
- https://git.kernel.org/stable/c/a0b4a0666beacfe8add9c71d8922475541dbae73
- https://git.kernel.org/stable/c/a7cb2e709f2927cc3c76781df3e45de2381b3b9d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53531.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53531
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
