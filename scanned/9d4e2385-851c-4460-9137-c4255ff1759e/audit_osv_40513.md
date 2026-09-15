# [H] nfsd: fix dead ACL conflict guard in nfsd4_create

## Summary
Severity: High
Advisory: CVE-2026-53395
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53395
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix dead ACL conflict guard in nfsd4_create

nfsd4_create() steals create->cr_dpacl/cr_pacl into the local
nfsd_attrs via the designated initializer, then immediately sets the
source pointers to NULL. The subsequent conflict guard tests the
already-nilled source fields, making it permanently dead code:

    if (create->cr_acl) {
        if (create->cr_dpacl || create->cr_pacl)  /* always false */

When a client encodes both FATTR4_WORD0_ACL and
FATTR4_WORD2_POSIX_{DEFAULT,ACCESS}_ACL in the same CREATE fattr
bitmap, nfsd4_acl_to_attr() overwrites attrs.na_pacl/na_dpacl without
releasing the originals, leaking two posix_acl slab objects per
request. Repeated requests cause unbounded slab exhaustion.

Fix by checking attrs.na_dpacl/na_pacl (the stolen values) instead of
the nilled create->cr_dpacl/cr_pacl, matching the correct pattern
already used in nfsd4_setattr().

## References
- https://git.kernel.org/stable/c/8371cc5c0a2cc2a71b3dcfd47ff1f7fcfc526a5e
- https://git.kernel.org/stable/c/a60f25a800846ab8e5a13f8a9d05111f2aee55a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53395.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
