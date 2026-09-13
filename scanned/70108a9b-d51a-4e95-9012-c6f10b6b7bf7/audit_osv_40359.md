# [H] NFSD: fix nfs4_file access extra count in nfsd4_add_rdaccess_to_wrdeleg

## Summary
Severity: High
Advisory: CVE-2026-53026
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53026
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: fix nfs4_file access extra count in nfsd4_add_rdaccess_to_wrdeleg

In nfsd4_add_rdaccess_to_wrdeleg, if fp->fi_fds[O_RDONLY] is already
set by another thread, __nfs4_file_get_access should not be called
to increment the nfs4_file access count since that was already done
by the thread that added READ access to the file. The extra fi_access
count in nfs4_file can prevent the corresponding nfsd_file from being
freed.

When stopping nfs-server service, these extra access counts trigger a
BUG in kmem_cache_destroy() that shows nfsd_file object remaining on
__kmem_cache_shutdown.

This problem can be reproduced by running the Git project's test
suite over NFS.

## References
- https://git.kernel.org/stable/c/4584229395d0d65bd517780afe97ffea07cb2c3d
- https://git.kernel.org/stable/c/b48f44f36e6607b2f818560f19deb86b4a9c717b
- https://git.kernel.org/stable/c/b81572b073441dfd32213e41857676d0dbff4665
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53026.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
