# [H] net: qrtr: Fix a refcount bug in qrtr_recvmsg()

## Summary
Severity: High
Advisory: CVE-2023-53445
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53445
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qrtr: Fix a refcount bug in qrtr_recvmsg()

Syzbot reported a bug as following:

refcount_t: addition on 0; use-after-free.
...
RIP: 0010:refcount_warn_saturate+0x17c/0x1f0 lib/refcount.c:25
...
Call Trace:
 <TASK>
 __refcount_add include/linux/refcount.h:199 [inline]
 __refcount_inc include/linux/refcount.h:250 [inline]
 refcount_inc include/linux/refcount.h:267 [inline]
 kref_get include/linux/kref.h:45 [inline]
 qrtr_node_acquire net/qrtr/af_qrtr.c:202 [inline]
 qrtr_node_lookup net/qrtr/af_qrtr.c:398 [inline]
 qrtr_send_resume_tx net/qrtr/af_qrtr.c:1003 [inline]
 qrtr_recvmsg+0x85f/0x990 net/qrtr/af_qrtr.c:1070
 sock_recvmsg_nosec net/socket.c:1017 [inline]
 sock_recvmsg+0xe2/0x160 net/socket.c:1038
 qrtr_ns_worker+0x170/0x1700 net/qrtr/ns.c:688
 process_one_work+0x991/0x15c0 kernel/workqueue.c:2390
 worker_thread+0x669/0x1090 kernel/workqueue.c:2537

It occurs in the concurrent scenario of qrtr_recvmsg() and
qrtr_endpoint_unregister() as following:

	cpu0					cpu1
qrtr_recvmsg				qrtr_endpoint_unregister
qrtr_send_resume_tx			qrtr_node_release
qrtr_node_lookup			mutex_lock(&qrtr_node_lock)
spin_lock_irqsave(&qrtr_nodes_lock, )	refcount_dec_and_test(&node->ref) [node->ref == 0]
radix_tree_lookup [node != NULL]	__qrtr_node_release
qrtr_node_acquire			spin_lock_irqsave(&qrtr_nodes_lock, )
kref_get(&node->ref) [WARNING]		...
					mutex_unlock(&qrtr_node_lock)

Use qrtr_node_lock to protect qrtr_node_lookup() implementation, this
is actually improving the protection of node reference.

## References
- https://git.kernel.org/stable/c/44d807320000db0d0013372ad39b53e12d52f758
- https://git.kernel.org/stable/c/48a07f6e00d305597396da4d7494b81cec05b9d3
- https://git.kernel.org/stable/c/98a9cd82c541ef6cbdb829cd6c05cbbb471e373c
- https://git.kernel.org/stable/c/aa95efa187b4114075f312b3c4680d050b56fdec
- https://git.kernel.org/stable/c/b9ba5906c42089f8e1d0001b7b50a7940f086cbb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53445.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53445
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
