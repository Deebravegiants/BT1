# [H] drm/xe/queue: Call fini on exec queue creation fail

## Summary
Severity: High
Advisory: CVE-2026-23350
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23350
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/queue: Call fini on exec queue creation fail

Every call to queue init should have a corresponding fini call.
Skipping this would mean skipping removal of the queue from GuC list
(which is part of guc_id allocation). A damaged queue stored in
exec_queue_lookup list would lead to invalid memory reference,
sooner or later.

Call fini to free guc_id. This must be done before any internal
LRCs are freed.

Since the finalization with this extra call became very similar to
__xe_exec_queue_fini(), reuse that. To make this reuse possible,
alter xe_lrc_put() so it can survive NULL parameters, like other
similar functions.

v2: Reuse _xe_exec_queue_fini(). Make xe_lrc_put() aware of NULLs.

(cherry picked from commit 393e5fea6f7d7054abc2c3d97a4cfe8306cd6079)

## References
- https://git.kernel.org/stable/c/99f9b5343cae80eb0dfe050baf6c86d722b3ba2e
- https://git.kernel.org/stable/c/fae65b8a4449ae556990efcde8d74bec4adc5925
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23350.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
