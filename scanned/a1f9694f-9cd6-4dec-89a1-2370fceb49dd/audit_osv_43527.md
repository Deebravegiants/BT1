# [H] NFSD: Handle layout stid in nfsd4_drop_revoked_stid()

## Summary
Severity: High
Advisory: CVE-2026-74316
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74316
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Handle layout stid in nfsd4_drop_revoked_stid()

nfsd4_drop_revoked_stid() has no SC_TYPE_LAYOUT case, so when a
client sends FREE_STATEID for an admin-revoked layout stid, the
default branch releases cl_lock and returns without unhashing or
releasing the stid.  The stid remains in the IDR and on the
per-client list until the client is destroyed.

Remove the layout stid from the per-client list and call
nfs4_put_stid() to drop the creation reference.  When the
refcount reaches zero, nfsd4_free_layout_stateid() handles the
remaining cleanup: cancelling the fence worker, removing from
the per-file list, and freeing the slab object.

## References
- https://git.kernel.org/stable/c/7ed62f7040ee182cf7dea5798f9e114235b31dae
- https://git.kernel.org/stable/c/8024028ef91616cf91cc669f2446a0406bc0ba19
- https://git.kernel.org/stable/c/86b9898920a6d02b4149f4fef9efd77b8aa3b9ca
- https://git.kernel.org/stable/c/da6f86ff4f2dd490bea52419a49e19680efd5847
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74316.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74316
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
