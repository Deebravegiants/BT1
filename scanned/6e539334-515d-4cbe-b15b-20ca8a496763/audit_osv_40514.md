# [H] nfsd: fix posix_acl leak and ignored error in nfsd4_create_file

## Summary
Severity: High
Advisory: CVE-2026-53396
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53396
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix posix_acl leak and ignored error in nfsd4_create_file

nfsd4_create_file() has two bugs in its ACL handling:

The return value of nfsd4_acl_to_attr() is silently discarded.  When
the NFSv4-to-POSIX ACL conversion fails (e.g., -EINVAL for
unsupported ACE types), the file is created without any ACL and the
client receives NFS4_OK.  This violates RFC 7530/8881 which require
the server to reject unsupported attributes on CREATE.

When start_creating() fails after ACL attributes have been populated
in attrs (either via nfsd4_acl_to_attr or via ownership transfer from
open->op_dpacl/op_pacl), the function jumps to out_write which skips
nfsd_attrs_free().  The posix_acl allocations are leaked.  A client
can trigger this repeatedly with OPEN(CREATE), ACL attributes, and an
invalid filename (e.g., longer than NAME_MAX).

Fix both by capturing the nfsd4_acl_to_attr() return value and by
changing the early error paths to jump to out instead of out_write.
Initialize child to ERR_PTR(-EINVAL) so that end_creating() is safe
to call even if start_creating() was never reached.

## References
- https://git.kernel.org/stable/c/18cf006a08babec0bbac2a3784f8f28e56e47490
- https://git.kernel.org/stable/c/24c975bbdd564d7d0ad90294bfa69729830345de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53396.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
