# [H] blk-mq: pop cached request if it is usable

## Summary
Severity: High
Advisory: CVE-2026-64017
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64017
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: pop cached request if it is usable

When submitting a bio to blk-mq, if the task should sleep after peeking
a cached request, but before it pops it, the plug flushes and calls
blk_mq_free_plug_rqs, freeing the cached_rqs. This creates a
use-after-free bug. Fix this by popping the cached request before any
possible blocking calls if it is suitable for use.

Popping this request first holds a queue reference, so avoid any
serialization races with queue freezes and can safely proceed with
dispatching that request to the driver. This potentially increases a
timing window from when a driver wants to freeze its queue to when
requests stop being dispatched. That scenario is off the fast path
though, and drivers need to appropriately handle requests during a
freeze request anyway.

The downside is the popped element needs to be individually freed when
we performed a bio plug merge. The cached request would have had to be
freed later anyway, but this patch does it inline with building the plug
list instead of after flushing it.

## References
- https://git.kernel.org/stable/c/23d8ea1e303b5f32d883757a4a707e791dbc9808
- https://git.kernel.org/stable/c/388468f7e7d1eab092cf2a39fdfb502e52019ec6
- https://git.kernel.org/stable/c/97e2d08de282ef76f84ab4ccd00f1acb3f5f999e
- https://git.kernel.org/stable/c/dc278e9bf2b9513a763353e6b9cc21e0f532954e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64017.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64017
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
