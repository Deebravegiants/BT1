# [H] bpf: Cancel special fields on map value recycle

## Summary
Severity: High
Advisory: CVE-2026-74314
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74314
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Cancel special fields on map value recycle

Map update and delete paths currently call bpf_obj_free_fields() when a
value is being replaced or recycled. That makes field destruction depend
on the context of the update/delete operation. For tracing programs this
can include NMI context, where referenced kptr destructors, uptr
unpinning, and graph root destruction are not generally safe.

Introduce bpf_obj_cancel_fields() for the reusable-value path. It only
performs NMI-safe cleanup for timer, workqueue, and task_work fields.
Fields that need full destruction are left attached to the recycled value
and are destroyed by the final cleanup path instead.

Switch array and hashtab update/delete/recycle paths to this cancel
helper. Keep bpf_obj_free_fields() for final map destruction and for
bpf_mem_alloc destructors. Preallocated hashtabs do not have allocator
destructors, so teardown continues to walk the normal and extra elements
and fully destroy their fields.

This deliberately relaxes the eager-free semantics of map update/delete
for special fields. Programs that relied on a recycled map slot becoming
empty immediately after update/delete were relying on behavior that
cannot be implemented safely from every BPF execution context without
offloading arbitrary destructors.

There is a chance this change breaks programs making assumptions
regarding the eager freeing of fields. If so, we can relax semantics to
cancellation only when irqs_disabled() is true in the future. However,
theoretically, map values that get reused eagerly already have weaker
guarantees as parallel users can recreate freed fields before the new
element becomes visible again.

## References
- https://git.kernel.org/stable/c/9ea734e2cc0143d7429ab7dc0b20c85e5836183c
- https://git.kernel.org/stable/c/a3a81d247651218e47153f2d2afd7aee236726fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74314.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
