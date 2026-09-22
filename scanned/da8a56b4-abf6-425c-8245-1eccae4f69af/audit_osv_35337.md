# [H] nfsd: fix nfsd_file reference leak in nfsd4_add_rdaccess_to_wrdeleg()

## Summary
Severity: High
Advisory: CVE-2025-71090
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71090
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix nfsd_file reference leak in nfsd4_add_rdaccess_to_wrdeleg()

nfsd4_add_rdaccess_to_wrdeleg() unconditionally overwrites
fp->fi_fds[O_RDONLY] with a newly acquired nfsd_file. However, if
the client already has a SHARE_ACCESS_READ open from a previous OPEN
operation, this action overwrites the existing pointer without
releasing its reference, orphaning the previous reference.

Additionally, the function originally stored the same nfsd_file
pointer in both fp->fi_fds[O_RDONLY] and fp->fi_rdeleg_file with
only a single reference. When put_deleg_file() runs, it clears
fi_rdeleg_file and calls nfs4_file_put_access() to release the file.

However, nfs4_file_put_access() only releases fi_fds[O_RDONLY] when
the fi_access[O_RDONLY] counter drops to zero. If another READ open
exists on the file, the counter remains elevated and the nfsd_file
reference from the delegation is never released. This potentially
causes open conflicts on that file.

Then, on server shutdown, these leaks cause __nfsd_file_cache_purge()
to encounter files with an elevated reference count that cannot be
cleaned up, ultimately triggering a BUG() in kmem_cache_destroy()
because there are still nfsd_file objects allocated in that cache.

## References
- https://git.kernel.org/stable/c/8072e34e1387d03102b788677d491e2bcceef6f5
- https://git.kernel.org/stable/c/c07dc84ed67c5a182273171639bacbbb87c12175
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71090.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71090
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
