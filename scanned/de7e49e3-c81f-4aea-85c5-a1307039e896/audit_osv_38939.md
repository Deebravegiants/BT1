# [H] RDMA/irdma: Fix double free related to rereg_user_mr

## Summary
Severity: High
Advisory: CVE-2026-43120
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43120
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.136, >=6.7.0 <6.18.24, >=6.13.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix double free related to rereg_user_mr

If IB_MR_REREG_TRANS is set during rereg_user_mr, the
umem will be released and a new one will be allocated
in irdma_rereg_mr_trans. If any step of irdma_rereg_mr_trans
fails after the new umem is allocated, it releases the umem,
but does not set iwmr->region to NULL. The problem is that
this failure is propagated to the user, who will then call
ibv_dereg_mr (as they should). Then, the dereg_mr path will
see a non-NULL umem and attempt to call ib_umem_release again.

Fix this by setting iwmr->region to NULL after ib_umem_release.

Fixed: 5ac388db27c4 ("RDMA/irdma: Add support to re-register a memory region")

## References
- https://git.kernel.org/stable/c/0c5d70bcb9d2275a1c8515a924016fcfeb4ab441
- https://git.kernel.org/stable/c/0f22c32141acdcda266b26cab2b830baf870f3e0
- https://git.kernel.org/stable/c/29a3edd7004bb635d299fb9bc6f0ea4ef13ed5a2
- https://git.kernel.org/stable/c/62298a48f8b8788ad8b8464e6ffdf1ddebd2217e
- https://git.kernel.org/stable/c/66964118f1f50ed85001c8fc9f7ab5bbdd021ee0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43120.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
