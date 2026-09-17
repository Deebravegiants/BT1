# [H] ntfs: avoid heap allocation for free-cluster readahead state

## Summary
Severity: High
Advisory: CVE-2026-72202
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72202
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: avoid heap allocation for free-cluster readahead state

get_nr_free_clusters() allocates a temporary file_ra_state before it
publishes the precomputed free cluster count, sets NVolFreeClusterKnown(),
and wakes vol->free_waitq. If that allocation fails, the worker returns
without setting the flag or waking waiters, so callers waiting for the free
count can block indefinitely.

The readahead state is only used synchronously while scanning the bitmap.
Keep it on the stack and pass it by address to the readahead helper. This
eliminates the early allocation failure path instead of adding a special
case that publishes a conservative count and wakes the waitqueue.
Zero-initialize the on-stack state because file_ra_state_init() only sets
ra_pages and prev_pos.

Apply the same treatment to __get_nr_free_mft_records(), which scans the
MFT bitmap with the same short-lived readahead state.

## References
- https://git.kernel.org/stable/c/40ee64e633e5e413f2255bb48c063977d8c86f34
- https://git.kernel.org/stable/c/c05132077df57a384919f61d7f8a8e76d748a6d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72202.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
