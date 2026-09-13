# [H] thunderbolt: Prevent XDomain delayed work use-after-free on disconnect

## Summary
Severity: High
Advisory: CVE-2026-74575
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74575
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Prevent XDomain delayed work use-after-free on disconnect

tb_xdp_handle_request() runs on system_wq and queues
xd->state_work via queue_delayed_work() in three request handlers:
PROPERTIES_CHANGED_REQUEST, UUID_REQUEST (via start_handshake),
and LINK_STATE_CHANGE_REQUEST.  Similarly, update_xdomain() queues
xd->properties_changed_work when local properties change.

Concurrently, tb_xdomain_remove() calls stop_handshake() which does
cancel_delayed_work_sync() on both delayed works.  Later,
tb_xdomain_unregister() calls device_unregister() which eventually
frees the xdomain.  Since commit 559c1e1e0134 ("thunderbolt: Run
tb_xdp_handle_request() in system workqueue") moved the request
handler off tb->wq, the handler and the remove path are no longer
serialized.  If queue_delayed_work() executes after
cancel_delayed_work_sync() but before the xdomain is freed, the
delayed work fires on a freed object.

Add xd->removing that tb_xdomain_remove() sets under xd->lock
before calling stop_handshake().  Each external queue site holds
the same lock and checks removing before calling
queue_delayed_work().  This provides the mutual exclusion needed:
either the queue site acquires the lock first and queues work that
the subsequent cancel will see, or the remove path acquires the
lock first and the queue site observes removing == true and skips
the queue.

## References
- https://git.kernel.org/stable/c/2aa2cde2cc79a79d8ea4a15be9f4a67fc528ae91
- https://git.kernel.org/stable/c/2c5d2d3c3f70cde2565d7b279b544893a2035842
- https://git.kernel.org/stable/c/33c0ee18cf8665c974b00f4e0ba769fbc07efe10
- https://git.kernel.org/stable/c/54a62153c765cd24239cde1f2633f2a2fd005368
- https://git.kernel.org/stable/c/91b40862a02000f490b63f1d315be3ee31e83871
- https://git.kernel.org/stable/c/cfbd2dba3d862c9be8c92bea2a357d9ed828a54a
- https://git.kernel.org/stable/c/d4fa0d544c04dea636bf821ff5582cd7d63e2c34
- https://git.kernel.org/stable/c/dc11d5118f9da6ea28487ffe055de5a0d0734125
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74575.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74575
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
