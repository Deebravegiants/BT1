# [H] io_uring: ensure ctx->rings is stable for task work flags manipulation

## Summary
Severity: High
Advisory: CVE-2026-23275
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23275
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: ensure ctx->rings is stable for task work flags manipulation

If DEFER_TASKRUN | SETUP_TASKRUN is used and task work is added while
the ring is being resized, it's possible for the OR'ing of
IORING_SQ_TASKRUN to happen in the small window of swapping into the
new rings and the old rings being freed.

Prevent this by adding a 2nd ->rings pointer, ->rings_rcu, which is
protected by RCU. The task work flags manipulation is inside RCU
already, and if the resize ring freeing is done post an RCU synchronize,
then there's no need to add locking to the fast path of task work
additions.

Note: this is only done for DEFER_TASKRUN, as that's the only setup mode
that supports ring resizing. If this ever changes, then they too need to
use the io_ctx_mark_taskrun() helper.

## References
- https://git.kernel.org/stable/c/46dc07d5f31411cc023f3bf1f4a23a07bf6e0ed1
- https://git.kernel.org/stable/c/7cc4530b3e952d4a5947e1e55d06620d8845d4f5
- https://git.kernel.org/stable/c/96189080265e6bb5dde3a4afbaf947af493e3f82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23275.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
