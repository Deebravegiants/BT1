# [C] nfs: use nfsi->rwsem to protect traversal of the file lock list

## Summary
Severity: Critical
Advisory: CVE-2026-72472
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72472
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs: use nfsi->rwsem to protect traversal of the file lock list

Lingfeng identified a bug and suggested two solutions, but both appear
to have issues.

Generally, we cannot release flc_lock while iterating over the file lock
list to avoid use-after-free (UAF) problems with file locks. However,
functions like nfs_delegation_claim_locks and nfs4_reclaim_locks cannot
adhere to this rule because recover_lock or nfs4_lock_delegation_recall
may take a long time. To resolve this, NFS switches to using nfsi->rwsem
for the same protection, and nfs_reclaim_locks follows this approach.
Although nfs_delegation_claim_locks uses so_delegreturn_mutex instead,
this is inadequate since a single inode can have multiple nfs4_state
instances. Therefore, the fix is to also use nfsi->rwsem in this case.

Furthermore, after commit c69899a17ca4 ("NFSv4: Update of VFS byte range
lock must be atomic with the stateid update"), the functions
nfs4_locku_done and nfs4_lock_done also break this rule because they
call locks_lock_inode_wait without holding nfsi->rwsem. Simply adding
this protection could cause many deadlocks, so instead, the call to
locks_lock_inode_wait is moved into _nfs4_proc_setlk. Regarding the bug
fixed by commit c69899a17ca4 ("NFSv4: Update of VFS byte range
lock must be atomic with the stateid update"), it has been resolved
after commit 0460253913e5 ("NFSv4: nfs4_do_open() is incorrectly triggering
state recovery") because all slots are drained before calling
nfs4_do_reclaim, which prevents concurrent stateid changes along this path.
Also, nfs_delegation_claim_locks does not cause this concurrency either
since when _nfs4_proc_setlk is called with NFS_DELEGATED_STATE, no RPC is
sent, so nfs4_lock_done is not called. Therefore,
nfs4_lock_delegation_recall from nfs_delegation_claim_locks is the first
time the stateid is set.

## References
- https://git.kernel.org/stable/c/1cda95bf2e9c0e6b63545b7565fe4a1e474322f4
- https://git.kernel.org/stable/c/4837fb36219e6c08b666bc31a86841bad8526358
- https://git.kernel.org/stable/c/e68035178e65e2b3aa386ce61202ff33724ae418
- https://git.kernel.org/stable/c/f161ef7b0dd2f51fdb002ba4a4e9bf0ee7409218
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72472.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72472
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
