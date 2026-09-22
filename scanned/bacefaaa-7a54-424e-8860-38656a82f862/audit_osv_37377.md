# [C] ksmbd: fix use-after-free and NULL deref in smb_grant_oplock()

## Summary
Severity: Critical
Advisory: CVE-2026-31444
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31444
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.130 <6.6.131, >=6.12.78 <6.12.80, >=6.18.19 <6.18.21, >=6.19.9 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free and NULL deref in smb_grant_oplock()

smb_grant_oplock() has two issues in the oplock publication sequence:

1) opinfo is linked into ci->m_op_list (via opinfo_add) before
   add_lease_global_list() is called.  If add_lease_global_list()
   fails (kmalloc returns NULL), the error path frees the opinfo
   via __free_opinfo() while it is still linked in ci->m_op_list.
   Concurrent m_op_list readers (opinfo_get_list, or direct iteration
   in smb_break_all_levII_oplock) dereference the freed node.

2) opinfo->o_fp is assigned after add_lease_global_list() publishes
   the opinfo on the global lease list.  A concurrent
   find_same_lease_key() can walk the lease list and dereference
   opinfo->o_fp->f_ci while o_fp is still NULL.

Fix by restructuring the publication sequence to eliminate post-publish
failure:

- Set opinfo->o_fp before any list publication (fixes NULL deref).
- Preallocate lease_table via alloc_lease_table() before opinfo_add()
  so add_lease_global_list() becomes infallible after publication.
- Keep the original m_op_list publication order (opinfo_add before
  lease list) so concurrent opens via same_client_has_lease() and
  opinfo_get_list() still see the in-flight grant.
- Use opinfo_put() instead of __free_opinfo() on err_out so that
  the RCU-deferred free path is used.

This also requires splitting add_lease_global_list() to take a
preallocated lease_table and changing its return type from int to void,
since it can no longer fail.

## References
- https://git.kernel.org/stable/c/48623ec358c1c600fa1e38368746f933e0f1a617
- https://git.kernel.org/stable/c/6d7e5a918c1d0aad06db0e17677b66fc9a471021
- https://git.kernel.org/stable/c/7de55bba69cbf0f9280daaea385daf08bc076121
- https://git.kernel.org/stable/c/9e785f004cbc56390479b77375726ea9b0d1a8a6
- https://git.kernel.org/stable/c/a5c6f6d6ceefed2d5210ee420fb75f8362461f46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31444.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31444
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
