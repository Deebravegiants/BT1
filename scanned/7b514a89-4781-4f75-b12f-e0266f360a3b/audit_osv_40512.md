# [H] nfsd: avoid leaking pre-allocated openowner on unconfirmed retry race

## Summary
Severity: High
Advisory: CVE-2026-53394
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53394
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: avoid leaking pre-allocated openowner on unconfirmed retry race

When find_or_alloc_open_stateowner() encounters an unconfirmed owner, it
calls release_openowner() and sets oo = NULL. Control then falls through
past the `if (oo)` guard -- which would have freed any pre-allocated
`new` -- and unconditionally executes `new = alloc_stateowner(...)`. If
`new` was already allocated on a prior iteration, the pointer is
silently overwritten and the previous allocation (slab object + owner
name buffer) is leaked.

This requires a race: two NFSv4.0 OPEN threads with the same owner
string, where a concurrent thread inserts a new unconfirmed owner into
the hash between retry iterations. The window is narrow but repeatable
under adversarial conditions.

Fix by adding `goto retry` after `oo = NULL` so the already-allocated
`new` is reused on the next iteration rather than overwritten.

## References
- https://git.kernel.org/stable/c/017a6150106b054cc84d1b0582d97bd3a74d4281
- https://git.kernel.org/stable/c/57aee7a35bb12753057c5b65d72d1f46c0e95b07
- https://git.kernel.org/stable/c/a10bf67fe06469a71a401f72f328237345d553c0
- https://git.kernel.org/stable/c/c9aefb2b5f11337c9202c5bd0c45d71198449718
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53394.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53394
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
