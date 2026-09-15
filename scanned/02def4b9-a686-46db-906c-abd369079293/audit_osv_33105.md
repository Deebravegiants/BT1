# [H] nfsd: allow SC_STATUS_FREEABLE when searching via nfs4_lookup_stateid()

## Summary
Severity: High
Advisory: CVE-2025-39688
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-39688
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: allow SC_STATUS_FREEABLE when searching via nfs4_lookup_stateid()

The pynfs DELEG8 test fails when run against nfsd. It acquires a
delegation and then lets the lease time out. It then tries to use the
deleg stateid and expects to see NFS4ERR_DELEG_REVOKED, but it gets
bad NFS4ERR_BAD_STATEID instead.

When a delegation is revoked, it's initially marked with
SC_STATUS_REVOKED, or SC_STATUS_ADMIN_REVOKED and later, it's marked
with the SC_STATUS_FREEABLE flag, which denotes that it is waiting for
s FREE_STATEID call.

nfs4_lookup_stateid() accepts a statusmask that includes the status
flags that a found stateid is allowed to have. Currently, that mask
never includes SC_STATUS_FREEABLE, which means that revoked delegations
are (almost) never found.

Add SC_STATUS_FREEABLE to the always-allowed status flags, and remove it
from nfsd4_delegreturn() since it's now always implied.

## References
- https://git.kernel.org/stable/c/52e209203c35a4fbff8af23cd3613efe5df40102
- https://git.kernel.org/stable/c/5bcb44e650bc4ec7eac23df90c5e011a77fa2beb
- https://git.kernel.org/stable/c/d1bc15b147d35b4cb7ca99a9a7d79d41ca342c13
- https://git.kernel.org/stable/c/dc6f3295905d7185e71091870119a8c11c3808cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39688.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39688
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
