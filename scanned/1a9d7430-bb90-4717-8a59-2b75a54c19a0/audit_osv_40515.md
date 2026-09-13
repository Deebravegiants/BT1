# [H] nfsd: fix posix_acl leak on SETACL decode failure

## Summary
Severity: High
Advisory: CVE-2026-53397
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53397
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix posix_acl leak on SETACL decode failure

nfsaclsvc_decode_setaclargs() and nfs3svc_decode_setaclargs() each
call nfs_stream_decode_acl() twice, first for NFS_ACL and then for
NFS_DFACL.  Each successful call transfers ownership of a freshly
allocated posix_acl into argp->acl_access or argp->acl_default.  If
the first call succeeds but the second fails, the decoder returns
false and argp->acl_access is left dangling.

ACLPROC2_SETACL.pc_release was wired to nfssvc_release_attrstat and
ACLPROC3_SETACL.pc_release was wired to nfs3svc_release_fhandle.
Both only call fh_put() and have no knowledge of the ACL fields on
argp.  The posix_acl_release() pairs sat at the out: labels inside
nfsacld_proc_setacl() and nfsd3_proc_setacl(), but svc_process()
skips pc_func when pc_decode returns false, so that cleanup is
unreachable on decode failure:

    svc_process_common()
      pc_decode()                  /* decode_setaclargs: false */
      /* pc_func skipped */
      pc_release()                 /* fh_put only -- ACLs leaked */

The orphaned posix_acl is leaked for the lifetime of the server.

Fix by adding nfsaclsvc_release_setacl() and nfs3svc_release_setacl(),
which release both argp->acl_access and argp->acl_default in addition
to fh_put(), and wiring them as pc_release for their respective SETACL
procedures.  pc_release runs on every path svc_process() takes after
decode, including decode failure, so the posix_acl_release() pairs are
removed from the proc functions' out: labels to keep ownership in one
place.  This matches the existing release_getacl() pattern used by
the sibling GETACL procedures.

## References
- https://git.kernel.org/stable/c/0853ac544c590880d797b04daa33fcb72b6be0e1
- https://git.kernel.org/stable/c/136b416593f1349cf6f72c8e3d18f0f204ee8545
- https://git.kernel.org/stable/c/1e96239fddcefacf6afe6c498357be68eacbcabc
- https://git.kernel.org/stable/c/887f92ceccf3eacd5f2402db21254d66372fae00
- https://git.kernel.org/stable/c/a5b42c1e4ff2befaa6b96f7cbf32174751eba083
- https://git.kernel.org/stable/c/b2eb1ffd511d1b3c3e21122f97cbbccea411e277
- https://git.kernel.org/stable/c/b94c4be77682aab06d65ca7296149e3bcfb37353
- https://git.kernel.org/stable/c/bd69a825485168ef74e815ecb286754b570fdcc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
