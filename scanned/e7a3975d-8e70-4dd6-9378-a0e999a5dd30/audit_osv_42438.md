# [H] iomap: fix out-of-bounds bitmap_set() with zero-length range

## Summary
Severity: High
Advisory: CVE-2026-68145
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68145
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.153, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

iomap: fix out-of-bounds bitmap_set() with zero-length range

ifs_set_range_dirty() and ifs_set_range_uptodate() compute last_blk
as (off + len - 1) >> i_blkbits.  When off is 0 and len is 0, the
unsigned subtraction underflows to SIZE_MAX, producing a huge
last_blk and nr_blks value that causes bitmap_set() to write far
beyond the ifs->state allocation.

Regarding ifs_set_range_uptodate(), it is temporarily safe because len
cannot be passed in as 0. However, for ifs_set_range_dirty() this is
reachable from __iomap_write_end(): when copy_folio_from_iter_atomic()
returns 0 (e.g. user buffer fault) and the folio is already uptodate,
the guard at the top of __iomap_write_end() does not trigger because
!folio_test_uptodate() is false, and iomap_set_range_dirty() is called
with copied == 0.

Add a !len guard to both functions before the computation, so that a
zero-length range is a no-op.

## References
- https://git.kernel.org/stable/c/48829622212f6b8f49155889aecc818ba28ba680
- https://git.kernel.org/stable/c/7037e7bdcd26f46c080b8ce307dee5cb471c4b7c
- https://git.kernel.org/stable/c/9c7d8f7c8994c790fca501dc45ce66e7356cbe05
- https://git.kernel.org/stable/c/c5b6a48a8a716a7730e39af1cad083dc4ec955ce
- https://git.kernel.org/stable/c/fb4fad9105c88b1d82f1b3c39e3b6abea8249af6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68145.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
