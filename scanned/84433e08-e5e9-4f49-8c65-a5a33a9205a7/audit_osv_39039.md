# [H] sched_ext: Remove redundant css_put() in scx_cgroup_init()

## Summary
Severity: High
Advisory: CVE-2026-43438
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43438
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: Remove redundant css_put() in scx_cgroup_init()

The iterator css_for_each_descendant_pre() walks the cgroup hierarchy
under cgroup_lock(). It does not increment the reference counts on
yielded css structs.

According to the cgroup documentation, css_put() should only be used
to release a reference obtained via css_get() or css_tryget_online().
Since the iterator does not use either of these to acquire a reference,
calling css_put() in the error path of scx_cgroup_init() causes a
refcount underflow.

Remove the unbalanced css_put() to prevent a potential Use-After-Free
(UAF) vulnerability.

## References
- https://git.kernel.org/stable/c/1336b579f6079fb8520be03624fcd9ba443c930b
- https://git.kernel.org/stable/c/6eaaa67d6998f6c30c462b140db8c062e07ec473
- https://git.kernel.org/stable/c/bf50f3285eda8a0173625fcdb5f183f96e1008cd
- https://git.kernel.org/stable/c/cc095cd305fddbe25a968e4a78436ff9476cf0f6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43438.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43438
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
