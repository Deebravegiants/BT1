# [H] nfsd: decrease sc_count directly if fail to queue dl_recall

## Summary
Severity: High
Advisory: CVE-2025-37871
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37871
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.236 <5.10.237, >=5.15.180 <5.15.181, >=6.1.134 <6.1.135, >=6.6.87 <6.6.88, >=6.12.23 <6.12.25, >=6.14.2 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: decrease sc_count directly if fail to queue dl_recall

A deadlock warning occurred when invoking nfs4_put_stid following a failed
dl_recall queue operation:
            T1                            T2
                                nfs4_laundromat
                                 nfs4_get_client_reaplist
                                  nfs4_anylock_blockers
__break_lease
 spin_lock // ctx->flc_lock
                                   spin_lock // clp->cl_lock
                                   nfs4_lockowner_has_blockers
                                    locks_owner_has_blockers
                                     spin_lock // flctx->flc_lock
 nfsd_break_deleg_cb
  nfsd_break_one_deleg
   nfs4_put_stid
    refcount_dec_and_lock
     spin_lock // clp->cl_lock

When a file is opened, an nfs4_delegation is allocated with sc_count
initialized to 1, and the file_lease holds a reference to the delegation.
The file_lease is then associated with the file through kernel_setlease.

The disassociation is performed in nfsd4_delegreturn via the following
call chain:
nfsd4_delegreturn --> destroy_delegation --> destroy_unhashed_deleg -->
nfs4_unlock_deleg_lease --> kernel_setlease --> generic_delete_lease
The corresponding sc_count reference will be released after this
disassociation.

Since nfsd_break_one_deleg executes while holding the flc_lock, the
disassociation process becomes blocked when attempting to acquire flc_lock
in generic_delete_lease. This means:
1) sc_count in nfsd_break_one_deleg will not be decremented to 0;
2) The nfs4_put_stid called by nfsd_break_one_deleg will not attempt to
acquire cl_lock;
3) Consequently, no deadlock condition is created.

Given that sc_count in nfsd_break_one_deleg remains non-zero, we can
safely perform refcount_dec on sc_count directly. This approach
effectively avoids triggering deadlock warnings.

## References
- https://git.kernel.org/stable/c/14985d66b9b99c12995dd99d1c6c8dec4114c2a5
- https://git.kernel.org/stable/c/7d192e27a431026c58d60edf66dc6cd98d0c01fc
- https://git.kernel.org/stable/c/a1d14d931bf700c1025db8c46d6731aa5cf440f9
- https://git.kernel.org/stable/c/a70832d3555987035fc430ccd703acd89393eadb
- https://git.kernel.org/stable/c/a7fce086f6ca84db409b9d58493ea77c1978897c
- https://git.kernel.org/stable/c/b9bbe8f9d5663311d06667ce36d6ed255ead1a26
- https://git.kernel.org/stable/c/ba903539fff745d592d893c71b30e5e268a95413
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37871.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37871
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
