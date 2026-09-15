# [H] nfsd: fix handling of cached open files in nfsd4_open codepath

## Summary
Severity: High
Advisory: CVE-2023-52909
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2023-52909
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: fix handling of cached open files in nfsd4_open codepath

Commit fb70bf124b05 ("NFSD: Instantiate a struct file when creating a
regular NFSv4 file") added the ability to cache an open fd over a
compound. There are a couple of problems with the way this currently
works:

It's racy, as a newly-created nfsd_file can end up with its PENDING bit
cleared while the nf is hashed, and the nf_file pointer is still zeroed
out. Other tasks can find it in this state and they expect to see a
valid nf_file, and can oops if nf_file is NULL.

Also, there is no guarantee that we'll end up creating a new nfsd_file
if one is already in the hash. If an extant entry is in the hash with a
valid nf_file, nfs4_get_vfs_file will clobber its nf_file pointer with
the value of op_file and the old nf_file will leak.

Fix both issues by making a new nfsd_file_acquirei_opened variant that
takes an optional file pointer. If one is present when this is called,
we'll take a new reference to it instead of trying to open the file. If
the nfsd_file already has a valid nf_file, we'll just ignore the
optional file and pass the nfsd_file back as-is.

Also rework the tracepoints a bit to allow for an "opened" variant and
don't try to avoid counting acquisitions in the case where we already
have a cached open file.

## References
- https://git.kernel.org/stable/c/0b3a551fa58b4da941efeb209b3770868e2eddd7
- https://git.kernel.org/stable/c/0b778361998d6c6356b8d2fc7ddf025fb3224654
- https://git.kernel.org/stable/c/45c08a752982116f3287afcd1bd9c50f4fab0c28
- https://git.kernel.org/stable/c/973acfdfe90c8a4e58ade97ff0653a498531ff2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52909.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52909
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
