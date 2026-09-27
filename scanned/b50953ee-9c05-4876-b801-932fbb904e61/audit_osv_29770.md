# [C] nfsd: fix nfsd4_deleg_getattr_conflict in presence of third party lease

## Summary
Severity: Critical
Advisory: CVE-2024-46690
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46690
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix nfsd4_deleg_getattr_conflict in presence of third party lease

It is not safe to dereference fl->c.flc_owner without first confirming
fl->fl_lmops is the expected manager.  nfsd4_deleg_getattr_conflict()
tests fl_lmops but largely ignores the result and assumes that flc_owner
is an nfs4_delegation anyway.  This is wrong.

With this patch we restore the "!= &nfsd_lease_mng_ops" case to behave
as it did before the change mentioned below.  This is the same as the
current code, but without any reference to a possible delegation.

## References
- https://git.kernel.org/stable/c/1b46a871e980e3daa16fd5e77539966492e8910a
- https://git.kernel.org/stable/c/40927f3d0972bf86357a32a5749be71a551241b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46690.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46690
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
