# [H] fuse-uring: fix data races on ring->ready

## Summary
Severity: High
Advisory: CVE-2026-64588
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64588
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse-uring: fix data races on ring->ready

On weakly-ordered architectures, the store to fiq->ops can be
reordered past the store to ring->ready, allowing a CPU that sees
ring->ready == true via fuse_uring_ready() to dispatch requests
through a stale fiq->ops pointer. Upgrade the store to
smp_store_release() and the load in fuse_uring_ready() to
smp_load_acquire() so that the preceding WRITE_ONCE(fiq->ops, ...)
is visible to any CPU that observes ring->ready == true.

Additionally, fuse_uring_do_register() publishes ring->ready with
WRITE_ONCE() but the fast-path check reads it with a plain load.
This is a marked-vs-unmarked access that KCSAN will flag. Wrap it in
READ_ONCE() to mark it without adding unnecessary ordering.

Also wrap the fc->ring load in fuse_uring_ready() in READ_ONCE() to
prevent the compiler from reloading it between the NULL check and the
dereference.

## References
- https://git.kernel.org/stable/c/46725a0056c884cf58a6897f222892807327d82d
- https://git.kernel.org/stable/c/b156bb9966972122b148acab8bdf415cdb8176a3
- https://git.kernel.org/stable/c/d01a09b442cb786cd44ccc7c84d57e2856d6737c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64588.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
