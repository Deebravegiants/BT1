# [C] SUNRPC: Bound-check xdr_buf_to_bvec() stores before writing

## Summary
Severity: Critical
Advisory: CVE-2026-72217
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72217
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Bound-check xdr_buf_to_bvec() stores before writing

xdr_buf_to_bvec() writes a bio_vec into the caller's array before
testing whether that slot is in range, and the head branch performs
the store with no check at all. When the caller's budget is exactly
used up, the next store lands one element past the end of the array.
The overflow label returns count - 1, which masks the surplus store
but cannot undo it.

rq_bvec, the array passed by nfsd_vfs_write(), is allocated to
exactly rq_maxpages entries with no slack. The OOB store can land in
adjacent slab memory; the bv_len and bv_offset fields written there
are derived from client-supplied RPC payload sizes.

Move the in-range check ahead of the store in the head, page-loop,
and tail branches. With the check at the top of each sequence, count
is incremented only after a successful store, so the overflow label
can return count directly.

## References
- https://git.kernel.org/stable/c/42f5b80dda6b86e424054baf1475df686c403d5c
- https://git.kernel.org/stable/c/4a1148f2739d5089c3ca8ae2e9d1053e219ab5df
- https://git.kernel.org/stable/c/6029e711a818bf34d6c4b90cafee24f3afffa110
- https://git.kernel.org/stable/c/69e18135e2a004a79505451dbef07314ea16e1eb
- https://git.kernel.org/stable/c/98414b42530af65cb984ffc12685096a3b5e179a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72217.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
