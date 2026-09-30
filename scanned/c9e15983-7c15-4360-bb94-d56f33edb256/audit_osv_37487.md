# [H] writeback: Fix use after free in inode_switch_wbs_work_fn()

## Summary
Severity: High
Advisory: CVE-2026-31703
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31703
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

writeback: Fix use after free in inode_switch_wbs_work_fn()

inode_switch_wbs_work_fn() has a loop like:

  wb_get(new_wb);
  while (1) {
    list = llist_del_all(&new_wb->switch_wbs_ctxs);
    /* Nothing to do? */
    if (!list)
      break;
    ... process the items ...
  }

Now adding of items to the list looks like:

wb_queue_isw()
  if (llist_add(&isw->list, &wb->switch_wbs_ctxs))
    queue_work(isw_wq, &wb->switch_work);

Because inode_switch_wbs_work_fn() loops when processing isw items, it
can happen that wb->switch_work is pending while wb->switch_wbs_ctxs is
empty. This is a problem because in that case wb can get freed (no isw
items -> no wb reference) while the work is still pending causing
use-after-free issues.

We cannot just fix this by cancelling work when freeing wb because that
could still trigger problematic 0 -> 1 transitions on wb refcount due to
wb_get() in inode_switch_wbs_work_fn(). It could be all handled with
more careful code but that seems unnecessarily complex so let's avoid
that until it is proven that the looping actually brings practical
benefit. Just remove the loop from inode_switch_wbs_work_fn() instead.
That way when wb_queue_isw() queues work, we are guaranteed we have
added the first item to wb->switch_wbs_ctxs and nobody is going to
remove it (and drop the wb reference it holds) until the queued work
runs.

## References
- https://git.kernel.org/stable/c/028103656b84273c73e9e271cf95c9f3421f4b8a
- https://git.kernel.org/stable/c/156cc63691c1f20905510b1007896e090355e6c2
- https://git.kernel.org/stable/c/19ec404b079be057b387643ba0c69bbcc5867c35
- https://git.kernel.org/stable/c/382cf81cae89e58d22b4bdc38891cd4d0b9ba921
- https://git.kernel.org/stable/c/6689f01d6740cf358932b3e97ee968c6099800d9
- https://git.kernel.org/stable/c/9223e5f30403a9b506d6d0bff4f2e29a2d7d46af
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31703.json
- https://access.redhat.com/security/cve/CVE-2026-31703
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31703
- https://bugzilla.redhat.com/show_bug.cgi?id=2464385
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
