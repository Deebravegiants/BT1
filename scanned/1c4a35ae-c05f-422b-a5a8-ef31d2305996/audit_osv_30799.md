# [H] binder: fix OOB in binder_add_freeze_work()

## Summary
Severity: High
Advisory: CVE-2024-56555
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56555
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: fix OOB in binder_add_freeze_work()

In binder_add_freeze_work() we iterate over the proc->nodes with the
proc->inner_lock held. However, this lock is temporarily dropped to
acquire the node->lock first (lock nesting order). This can race with
binder_deferred_release() which removes the nodes from the proc->nodes
rbtree and adds them into binder_dead_nodes list. This leads to a broken
iteration in binder_add_freeze_work() as rb_next() will use data from
binder_dead_nodes, triggering an out-of-bounds access:

  ==================================================================
  BUG: KASAN: global-out-of-bounds in rb_next+0xfc/0x124
  Read of size 8 at addr ffffcb84285f7170 by task freeze/660

  CPU: 8 UID: 0 PID: 660 Comm: freeze Not tainted 6.11.0-07343-ga727812a8d45 #18
  Hardware name: linux,dummy-virt (DT)
  Call trace:
   rb_next+0xfc/0x124
   binder_add_freeze_work+0x344/0x534
   binder_ioctl+0x1e70/0x25ac
   __arm64_sys_ioctl+0x124/0x190

  The buggy address belongs to the variable:
   binder_dead_nodes+0x10/0x40
  [...]
  ==================================================================

This is possible because proc->nodes (rbtree) and binder_dead_nodes
(list) share entries in binder_node through a union:

	struct binder_node {
	[...]
		union {
			struct rb_node rb_node;
			struct hlist_node dead_node;
		};

Fix the race by checking that the proc is still alive. If not, simply
break out of the iteration.

## References
- https://git.kernel.org/stable/c/011e69a1b23011c0db3af4b8293fdd4522cc97b0
- https://git.kernel.org/stable/c/6b1be1da1f8279cf091266e71b5153c5b02aaff6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56555.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
