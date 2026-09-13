# [H] media: iris: fix use-after-free of fmt_src during MBPF check

## Summary
Severity: High
Advisory: CVE-2026-46210
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46210
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: iris: fix use-after-free of fmt_src during MBPF check

During concurrency testing, multiple instances can run in parallel, and
each instance uses its own inst->lock while the core->lock protects the
list of active instances. The race happens because these locks cover
different scopes, inst->lock protects only the internals of a single
instance, while the Macro Blocks Per Frame (MBPF) checker walks the
core list under core->lock and reads fields like fmt_src->width and
fmt_src->height. At the same time, iris_close() may free fmt_src and
fmt_dst under inst->lock while the instance is still present in the core
list. This allows a situation where the MBPF checker, still iterating
through the core list, reaches an instance whose fmt_src was already
freed by another thread and ends up dereferencing a dangling pointer,
resulting in a use-after-free. This happens because the MBPF checker
assumes that any instance in the core list is fully valid, but the
freeing of fmt_src and fmt_dst without removing the instance from the
core list is not correct.

The correct ordering is to defer freeing fmt_src and fmt_dst until after
the instance has been removed from the core list and all teardown under
the core lock has completed, ensuring that no dangling pointers are ever
exposed during MBPF checks.

## References
- https://git.kernel.org/stable/c/3d9593ad1a58c5acc3e5fa2a48222bb7632e6812
- https://git.kernel.org/stable/c/494ffd1712a588e590e6b1e9f876a8c8b24a9180
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46210
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
