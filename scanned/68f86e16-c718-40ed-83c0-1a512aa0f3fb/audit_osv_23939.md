# [M] 9p: fix fid refcount leak in v9fs_vfs_get_link

## Summary
Severity: Medium
Advisory: CVE-2022-49704
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49704
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: fix fid refcount leak in v9fs_vfs_get_link

we check for protocol version later than required, after a fid has
been obtained. Just move the version check earlier.

## References
- https://git.kernel.org/stable/c/e5690f263208c5abce7451370b7786eb25b405eb
- https://git.kernel.org/stable/c/e7b6d622bd812013eb39c8f4cd65b7ee8ede1e02
- https://git.kernel.org/stable/c/f0126bcaee81dabc1926012126aa74caa03a4c6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49704.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49704
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
