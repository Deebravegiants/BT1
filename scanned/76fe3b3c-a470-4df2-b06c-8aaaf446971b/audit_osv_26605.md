# [M] shmem: use ramfs_kill_sb() for kill_sb method of ramfs-based tmpfs

## Summary
Severity: Medium
Advisory: CVE-2023-53391
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53391
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

shmem: use ramfs_kill_sb() for kill_sb method of ramfs-based tmpfs

As the ramfs-based tmpfs uses ramfs_init_fs_context() for the
init_fs_context method, which allocates fc->s_fs_info, use ramfs_kill_sb()
to free it and avoid a memory leak.

## References
- https://git.kernel.org/stable/c/1f34bf8b442c6d720e7fa6f15e8702427e48aea9
- https://git.kernel.org/stable/c/36ce9d76b0a93bae799e27e4f5ac35478c676592
- https://git.kernel.org/stable/c/487f229efea80c00dd7397547ec4f25fb8999d99
- https://git.kernel.org/stable/c/5fada375113767b3b57f1b04f7a4fe64ffaa626f
- https://git.kernel.org/stable/c/ebe07db840992a3886694ac3d303b06f4b70ce00
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53391.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
