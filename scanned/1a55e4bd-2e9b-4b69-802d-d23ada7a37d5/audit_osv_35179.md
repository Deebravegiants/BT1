# [H] NFSD: NFSv4 file creation neglects setting ACL

## Summary
Severity: High
Advisory: CVE-2025-68803
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68803
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.0.0 <6.6.121, >=6.2.0 <6.12.64, >=6.7.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: NFSv4 file creation neglects setting ACL

An NFSv4 client that sets an ACL with a named principal during file
creation retrieves the ACL afterwards, and finds that it is only a
default ACL (based on the mode bits) and not the ACL that was
requested during file creation. This violates RFC 8881 section
6.4.1.3: "the ACL attribute is set as given".

The issue occurs in nfsd_create_setattr(), which calls
nfsd_attrs_valid() to determine whether to call nfsd_setattr().
However, nfsd_attrs_valid() checks only for iattr changes and
security labels, but not POSIX ACLs. When only an ACL is present,
the function returns false, nfsd_setattr() is skipped, and the
POSIX ACL is never applied to the inode.

Subsequently, when the client retrieves the ACL, the server finds
no POSIX ACL on the inode and returns one generated from the file's
mode bits rather than returning the originally-specified ACL.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/214b396480061cbc8b16f2c518b2add7fbfa5192
- https://git.kernel.org/stable/c/381261f24f4e4b41521c0e5ef5cc0b9a786a9862
- https://git.kernel.org/stable/c/60dbdef2ebc2317266a385e4debdb1bb0e57afe1
- https://git.kernel.org/stable/c/75f91534f9acdfef77f8fa094313b7806f801725
- https://git.kernel.org/stable/c/913f7cf77bf14c13cfea70e89bcb6d0b22239562
- https://git.kernel.org/stable/c/bf4e671c651534a307ab2fabba4926116beef8c3
- https://git.kernel.org/stable/c/c182e1e0b7640f6bcc0c5ca8d473f7c57199ea3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68803.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68803
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
