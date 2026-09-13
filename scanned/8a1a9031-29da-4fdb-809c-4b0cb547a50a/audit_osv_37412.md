# [H] xfrm: prevent policy_hthresh.work from racing with netns teardown

## Summary
Severity: High
Advisory: CVE-2026-31516
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31516
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: prevent policy_hthresh.work from racing with netns teardown

A XFRM_MSG_NEWSPDINFO request can queue the per-net work item
policy_hthresh.work onto the system workqueue.

The queued callback, xfrm_hash_rebuild(), retrieves the enclosing
struct net via container_of(). If the net namespace is torn down
before that work runs, the associated struct net may already have
been freed, and xfrm_hash_rebuild() may then dereference stale memory.

xfrm_policy_fini() already flushes policy_hash_work during teardown,
but it does not synchronize policy_hthresh.work.

Synchronize policy_hthresh.work in xfrm_policy_fini() as well, so the
queued work cannot outlive the net namespace teardown and access a
freed struct net.

## References
- https://git.kernel.org/stable/c/29fe3a61bcdce398ee3955101c39f89c01a8a77e
- https://git.kernel.org/stable/c/4e2e77843fef473ef47e322d52436d8308582a96
- https://git.kernel.org/stable/c/56ea2257b83ee29a543f158159e3d1abc1e3e4fe
- https://git.kernel.org/stable/c/8854e9367465d784046362698731c1111e3b39b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31516.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31516
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
