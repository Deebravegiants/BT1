# [H] futex: Drop CLONE_THREAD requirement for private default hash alloc

## Summary
Severity: High
Advisory: CVE-2026-52973
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52973
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

futex: Drop CLONE_THREAD requirement for private default hash alloc

Currently need_futex_hash_allocate_default() depends on strict pthread
semantics, abusing CLONE_THREAD.  This breaks the non-concurrency
assumptions when doing the mm->futex_ref pcpu allocations, leading to
bugs[0] when sharing the mm in other ways; ie:

    BUG: KASAN: slab-use-after-free in futex_hash_put

... where the +1 bias can end up on a percpu counter that mm->futex_ref
no longer points at.

Loosen the check to cover any CLONE_VM clone, except vfork().  Excluding
vfork keeps the existing paths untouched (no overhead), and we can't
race in the first place: either the parent is suspended and the child
runs alone, or mm->futex_ref is already allocated from an earlier
CLONE_VM.

## References
- https://git.kernel.org/stable/c/1dcd36420af2da5bd59306dba9caf78e3d248b1d
- https://git.kernel.org/stable/c/974ac49a9a068b0591a59f65c63eb06579a13091
- https://git.kernel.org/stable/c/ee9dce44362b2d8132c32964656ab6dff7dfbc6a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-52973.json
- https://access.redhat.com/errata/RHSA-2026:45114
- https://access.redhat.com/errata/RHSA-2026:47040
- https://access.redhat.com/errata/RHSA-2026:62640
- https://access.redhat.com/errata/RHSA-2026:62642
- https://access.redhat.com/security/cve/CVE-2026-52973
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52973.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52973
- https://bugzilla.redhat.com/show_bug.cgi?id=2492413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
